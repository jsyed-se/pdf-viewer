import json
import time
from datetime import datetime, timezone
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

ROOT = Path(__file__).resolve().parents[3]
APP = "http://127.0.0.1:5173"
FIXTURES = ROOT / "A" / "tests" / "fixtures" / "generated"
LOG_DIR = ROOT / "C" / "evidence" / "logs"
RESULT = LOG_DIR / "firefox-phase2-d09-correction.json"
COMBINED = LOG_DIR / "firefox-phase2-d09-correction-geckodriver.log"
PARTS = [LOG_DIR / f"firefox-phase2-d09-correction-geckodriver-part-{i}.log" for i in (1, 2)]
GECKO = Path.home() / ".cache" / "selenium" / "geckodriver" / "win64" / "0.37.1" / "geckodriver.exe"


def start(log):
    options = Options()
    options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"
    options.add_argument("-headless")
    options.add_argument("-no-remote")
    service = Service(executable_path=str(GECKO), log_output=str(log), service_args=["--log", "info"])
    driver = webdriver.Firefox(options=options, service=service)
    driver.set_window_rect(width=1440, height=900)
    return driver, WebDriverWait(driver, 40)


def capture(driver):
    driver.execute_script(
        """
        window.__correctionErrors=[];
        const s=v=>{try{return typeof v==='string'?v:JSON.stringify(v)}catch(_){return String(v)}};
        const old=console.error.bind(console);
        console.error=(...a)=>{window.__correctionErrors.push({kind:'console.error',message:a.map(s).join(' ')});old(...a)};
        window.addEventListener('error',e=>window.__correctionErrors.push({kind:'window.error',message:e.message||String(e.error)}));
        window.addEventListener('unhandledrejection',e=>window.__correctionErrors.push({kind:'unhandledrejection',message:s(e.reason)}));
        """
    )


def errors(driver):
    try:
        return driver.execute_script("return window.__correctionErrors || []")
    except Exception:
        return []


def open_local(driver, name):
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "local-pdf-file"))).send_keys(str(FIXTURES / name))


for path in [RESULT, COMBINED, *PARTS]:
    if path.exists():
        path.unlink()

results = {}
browser = None

# D09 correction: replacement is quiet/page 1; deliberate scroll then advances tracking.
driver, wait = start(PARTS[0])
try:
    browser = {"name": driver.capabilities.get("browserName"), "version": driver.capabilities.get("browserVersion"), "platform": driver.capabilities.get("platformName"), "headless": True, "viewport": "1440x900"}
    driver.get(f"{APP}/tests/harness.html?dual=1")
    wait.until(lambda d: "primary:ready:normal.pdf:2" in d.find_element(By.CSS_SELECTOR, ".harness-log output").text)
    wait.until(lambda d: "secondary:ready:merge-beta.pdf:2" in d.find_element(By.CSS_SELECTOR, ".harness-log output").text)
    capture(driver)
    time.sleep(1.5)
    before = driver.find_element(By.CSS_SELECTOR, ".harness-log output").text.splitlines()
    driver.find_element(By.XPATH, '//button[normalize-space(.)="Replace primary bytes"]').click()
    wait.until(lambda d: "primary:ready:multi-page-text.pdf:16" in d.find_element(By.CSS_SELECTOR, ".harness-log output").text)
    time.sleep(2)
    after_replace = driver.find_element(By.CSS_SELECTOR, ".harness-log output").text.splitlines()
    replacement_delta = after_replace[len(before):]
    hosts = driver.find_elements(By.CSS_SELECTOR, ".sdk-host")
    primary_input = hosts[0].find_element(By.CSS_SELECTOR, 'input[aria-label="Current page"]')
    secondary_input = hosts[1].find_element(By.CSS_SELECTOR, 'input[aria-label="Current page"]')
    replacement_primary_page = primary_input.get_attribute("value")
    replacement_secondary = {"pageCount": secondary_input.get_attribute("max"), "currentPage": secondary_input.get_attribute("value")}
    replacement_page_callbacks = [line for line in replacement_delta if line.startswith("primary:page:")]
    replacement_secondary_events = [line for line in replacement_delta if line.startswith("secondary:")]
    workspace = hosts[0].find_element(By.CSS_SELECTOR, ".page-workspace")
    workspace_before_scroll = driver.execute_script(
        "return {clientHeight: arguments[0].clientHeight, scrollHeight: arguments[0].scrollHeight, scrollTop: arguments[0].scrollTop}",
        workspace,
    )
    driver.execute_script("arguments[0].scrollTop = Math.min(arguments[0].scrollHeight - arguments[0].clientHeight, 3200)", workspace)
    wait.until(lambda d: int(primary_input.get_attribute("value")) > 1)
    time.sleep(1)
    after_scroll = driver.find_element(By.CSS_SELECTOR, ".harness-log output").text.splitlines()
    scroll_delta = after_scroll[len(after_replace):]
    tracked_page = int(primary_input.get_attribute("value"))
    scroll_callbacks = [line for line in scroll_delta if line.startswith("primary:page:")]
    workspace_after_scroll = driver.execute_script(
        "return {clientHeight: arguments[0].clientHeight, scrollHeight: arguments[0].scrollHeight, scrollTop: arguments[0].scrollTop}",
        workspace,
    )
    app_errors = errors(driver)
    passed = replacement_primary_page == "1" and not replacement_page_callbacks and not replacement_secondary_events and replacement_secondary == {"pageCount": "2", "currentPage": "1"} and tracked_page > 1 and bool(scroll_callbacks) and not app_errors
    results["D09"] = {
        "outcome": "PASS" if passed else "FAIL",
        "replacementEvents": replacement_delta,
        "replacementPrimaryPage": int(replacement_primary_page),
        "replacementPageCallbackCount": len(replacement_page_callbacks),
        "secondaryEventsDuringReplacementCount": len(replacement_secondary_events),
        "secondaryAfterReplacement": {"pageCount": int(replacement_secondary["pageCount"]), "currentPage": int(replacement_secondary["currentPage"])},
        "workspaceBeforeDeliberateScroll": workspace_before_scroll,
        "postScrollEvents": scroll_delta,
        "postScrollTrackedPage": tracked_page,
        "postScrollPageCallbackCount": len(scroll_callbacks),
        "workspaceAfterDeliberateScroll": workspace_after_scroll,
        "capturedAppErrors": app_errors,
    }
except Exception as exc:
    results["D09"] = {"outcome": "FAIL", "exception": f"{type(exc).__name__}: {exc}", "capturedAppErrors": errors(driver)}
finally:
    driver.quit()

# D12 loaded -> loaded smoke after the D09 correction.
driver, wait = start(PARTS[1])
try:
    driver.get(f"{APP}/?correction=d12-smoke")
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".source-controls")))
    capture(driver)
    sequence = [("normal.pdf", "2"), ("multi-page-text.pdf", "16"), ("existing-annotations.pdf", "2"), ("normal.pdf", "2")]
    completed = []
    for name, count in sequence:
        open_local(driver, name)
        wait.until(lambda d, expected=count: d.find_element(By.CSS_SELECTOR, 'input[aria-label="Current page"]').get_attribute("max") == expected)
        completed.append(name)
        time.sleep(0.25)
    time.sleep(2)
    app_errors = errors(driver)
    final_page = driver.find_element(By.CSS_SELECTOR, 'input[aria-label="Current page"]').get_attribute("value")
    results["D12_loaded_to_loaded_smoke"] = {
        "outcome": "PASS" if completed == [x[0] for x in sequence] and final_page == "1" and not app_errors else "FAIL",
        "sequence": [x[0] for x in sequence],
        "completed": completed,
        "finalCurrentPage": int(final_page),
        "capturedAppErrors": app_errors,
    }
except Exception as exc:
    results["D12_loaded_to_loaded_smoke"] = {"outcome": "FAIL", "exception": f"{type(exc).__name__}: {exc}", "capturedAppErrors": errors(driver)}
finally:
    driver.quit()

time.sleep(0.5)
part_text = [path.read_text(encoding="utf-8", errors="replace") if path.exists() else "" for path in PARTS]
combined = "\n".join(part_text)
COMBINED.write_text(combined, encoding="utf-8")
send_lines = [line for line in combined.splitlines() if "sendWithPromise" in line]
app_js_lines = [line for line in combined.splitlines() if "JavaScript error:" in line and "resource://" not in line]
for result in results.values():
    if send_lines or app_js_lines:
        result["outcome"] = "FAIL"
payload = {
    "runAtUtc": datetime.now(timezone.utc).isoformat(),
    "browser": browser,
    "fixtureManifestHashes": {"normal.pdf": "0aef5927…", "large-linearized.pdf": "abf38a01…"},
    "results": results,
    "summary": {"passed": sum(v["outcome"] == "PASS" for v in results.values()), "failed": sum(v["outcome"] == "FAIL" for v in results.values()), "sendWithPromiseCount": len(send_lines), "applicationJavaScriptErrorCount": len(app_js_lines)},
    "combinedGeckodriverLog": str(COMBINED.relative_to(ROOT)),
    "partLogs": [str(path.relative_to(ROOT)) for path in PARTS],
    "sendWithPromiseLines": send_lines,
    "applicationJavaScriptErrorLines": app_js_lines,
}
RESULT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
