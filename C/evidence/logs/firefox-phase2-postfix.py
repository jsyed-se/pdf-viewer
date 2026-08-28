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
LOG_DIR = ROOT / "C" / "evidence" / "logs"
FIXTURES = ROOT / "A" / "tests" / "fixtures" / "generated"
APP = "http://127.0.0.1:5173"
SLOW = "http://127.0.0.1:8765/slow-no-range/large-linearized.pdf"
RESULT = LOG_DIR / "firefox-phase2-postfix.json"
COMBINED_LOG = LOG_DIR / "firefox-phase2-postfix-geckodriver.log"
PART_LOGS = [LOG_DIR / f"firefox-phase2-postfix-geckodriver-part-{index}.log" for index in range(1, 5)]
GECKO = Path.home() / ".cache" / "selenium" / "geckodriver" / "win64" / "0.37.1" / "geckodriver.exe"


def new_driver(log_path):
    options = Options()
    options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"
    options.add_argument("-headless")
    options.add_argument("-no-remote")
    service = Service(executable_path=str(GECKO), log_output=str(log_path), service_args=["--log", "info"])
    browser = webdriver.Firefox(options=options, service=service)
    browser.set_window_rect(width=1440, height=900)
    return browser, WebDriverWait(browser, 40)


def install_capture(browser):
    browser.execute_script(
        """
        window.__postfixErrors = [];
        const stringify = value => { try { return typeof value === 'string' ? value : JSON.stringify(value); } catch (_) { return String(value); } };
        const originalError = console.error.bind(console);
        console.error = (...args) => { window.__postfixErrors.push({kind:'console.error', message:args.map(stringify).join(' ')}); originalError(...args); };
        window.addEventListener('error', event => window.__postfixErrors.push({kind:'window.error', message:event.message || String(event.error)}));
        window.addEventListener('unhandledrejection', event => window.__postfixErrors.push({kind:'unhandledrejection', message:stringify(event.reason)}));
        """
    )


def captured(browser):
    try:
        return browser.execute_script("return window.__postfixErrors || []")
    except Exception:
        return []


def open_local(browser, name):
    WebDriverWait(browser, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '#local-pdf-file'))
    ).send_keys(str(FIXTURES / name))


def submit_url(browser, url):
    field = WebDriverWait(browser, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[aria-label="Remote PDF URL"]')))
    field.clear()
    field.send_keys(url)
    browser.find_element(By.CSS_SELECTOR, '.source-controls button[type="submit"]').click()


for path in [RESULT, COMBINED_LOG, *PART_LOGS]:
    if path.exists():
        path.unlink()

results = {}
capabilities = None

# D12a: loaded -> loaded replacement stress.
driver, wait = new_driver(PART_LOGS[0])
try:
    capabilities = {
        "name": driver.capabilities.get("browserName"),
        "version": driver.capabilities.get("browserVersion"),
        "platform": driver.capabilities.get("platformName"),
        "headless": True,
        "viewport": "1440x900",
    }
    driver.get(f"{APP}/?postfix=d12-loaded")
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".source-controls")))
    install_capture(driver)
    sequence = ["normal.pdf", "multi-page-text.pdf", "existing-annotations.pdf", "normal.pdf", "multi-page-text.pdf"]
    completed = []
    open_local(driver, sequence[0]); completed.append(sequence[0])
    wait.until(lambda d: d.find_element(By.CSS_SELECTOR, 'input[aria-label="Current page"]').get_attribute("max") == "2")
    open_local(driver, sequence[1]); completed.append(sequence[1])
    wait.until(lambda d: d.find_element(By.CSS_SELECTOR, 'input[aria-label="Current page"]').get_attribute("max") == "16")
    workspace = driver.find_element(By.CSS_SELECTOR, ".page-workspace")
    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", workspace)
    for name in sequence[2:]:
        time.sleep(0.15)
        open_local(driver, name); completed.append(name)
    wait.until(lambda d: d.find_element(By.CSS_SELECTOR, 'input[aria-label="Current page"]').get_attribute("max") == "16")
    time.sleep(3)
    errors = captured(driver)
    current = driver.find_element(By.CSS_SELECTOR, 'input[aria-label="Current page"]').get_attribute("value")
    summary = driver.find_element(By.CSS_SELECTOR, ".attachment-summary small").text
    results["D12_loaded_to_loaded"] = {
        "outcome": "PASS" if completed == sequence and current == "1" and "16 pages ready" in summary and not errors else "FAIL",
        "sequence": sequence,
        "completed": completed,
        "currentPage": current,
        "status": summary,
        "capturedAppErrors": errors,
    }
except Exception as error:
    results["D12_loaded_to_loaded"] = {"outcome": "FAIL", "exception": f"{type(error).__name__}: {error}", "capturedAppErrors": captured(driver)}
finally:
    driver.quit()

# D12b: loading -> loading replacement, then cancel the replacement.
driver, wait = new_driver(PART_LOGS[1])
try:
    driver.get(f"{APP}/?postfix=d12-loading")
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".source-controls")))
    install_capture(driver)
    first_url = f"{SLOW}?attempt=one"
    second_url = f"{SLOW}?attempt=two"
    submit_url(driver, first_url)
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".loading-panel")))
    submit_url(driver, second_url)
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".loading-panel")))
    time.sleep(1)
    driver.find_element(By.XPATH, '//button[normalize-space(.)="Cancel loading"]').click()
    wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".loading-panel")))
    time.sleep(2)
    errors = captured(driver)
    status = driver.find_element(By.CSS_SELECTOR, ".sr-status").get_attribute("textContent").strip()
    results["D12_loading_to_loading"] = {
        "outcome": "PASS" if status == "Loading cancelled." and not errors and not driver.find_elements(By.CSS_SELECTOR, ".viewer-toolbar") else "FAIL",
        "firstUrl": first_url,
        "replacementUrl": second_url,
        "statusAfterReplacementCancel": status,
        "documentNotInstalled": not bool(driver.find_elements(By.CSS_SELECTOR, ".viewer-toolbar")),
        "capturedAppErrors": errors,
    }
except Exception as error:
    results["D12_loading_to_loading"] = {"outcome": "FAIL", "exception": f"{type(error).__name__}: {error}", "capturedAppErrors": captured(driver)}
finally:
    driver.quit()

# D11: explicit cancellation of a slow no-range load.
driver, wait = new_driver(PART_LOGS[2])
try:
    driver.get(f"{APP}/?postfix=d11")
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".source-controls")))
    install_capture(driver)
    submit_url(driver, SLOW)
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".loading-panel")))
    cancel_started = time.perf_counter()
    driver.find_element(By.XPATH, '//button[normalize-space(.)="Cancel loading"]').click()
    wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".loading-panel")))
    latency = round((time.perf_counter() - cancel_started) * 1000, 1)
    time.sleep(4)
    status = driver.find_element(By.CSS_SELECTOR, ".sr-status").get_attribute("textContent").strip()
    errors = captured(driver)
    absent = not bool(driver.find_elements(By.CSS_SELECTOR, ".viewer-toolbar"))
    results["D11"] = {
        "outcome": "PASS" if status == "Loading cancelled." and absent and not errors else "FAIL",
        "url": SLOW,
        "cancelLatencyMs": latency,
        "status": status,
        "documentNotInstalledAfter4s": absent,
        "capturedAppErrors": errors,
    }
except Exception as error:
    results["D11"] = {"outcome": "FAIL", "exception": f"{type(error).__name__}: {error}", "capturedAppErrors": captured(driver)}
finally:
    driver.quit()

# D09: callback stability and dual-instance isolation.
driver, wait = new_driver(PART_LOGS[3])
try:
    driver.get(f"{APP}/tests/harness.html?dual=1")
    wait.until(lambda d: "primary:ready:normal.pdf:2" in d.find_element(By.CSS_SELECTOR, ".harness-log output").text)
    wait.until(lambda d: "secondary:ready:merge-beta.pdf:2" in d.find_element(By.CSS_SELECTOR, ".harness-log output").text)
    install_capture(driver)
    time.sleep(1.5)
    before = driver.find_element(By.CSS_SELECTOR, ".harness-log output").text.splitlines()
    driver.find_element(By.XPATH, '//button[normalize-space(.)="Replace primary bytes"]').click()
    wait.until(lambda d: "primary:ready:multi-page-text.pdf:16" in d.find_element(By.CSS_SELECTOR, ".harness-log output").text)
    time.sleep(3)
    after = driver.find_element(By.CSS_SELECTOR, ".harness-log output").text.splitlines()
    delta = after[len(before):]
    hosts = driver.find_elements(By.CSS_SELECTOR, ".sdk-host")
    states = []
    for host in hosts:
        page_input = host.find_element(By.CSS_SELECTOR, 'input[aria-label="Current page"]')
        states.append({"pageCount": int(page_input.get_attribute("max")), "currentPage": int(page_input.get_attribute("value"))})
    page_callbacks = [line for line in delta if line.startswith("primary:page:")]
    secondary_events = [line for line in delta if line.startswith("secondary:")]
    errors = captured(driver)
    passed = "primary:ready:multi-page-text.pdf:16" in delta and not page_callbacks and not secondary_events and states == [{"pageCount": 16, "currentPage": 1}, {"pageCount": 2, "currentPage": 1}] and not errors
    results["D09"] = {
        "outcome": "PASS" if passed else "FAIL",
        "replacementEvents": delta,
        "spuriousPrimaryPageCallbackCount": len(page_callbacks),
        "secondaryEventCountDuringPrimaryReplacement": len(secondary_events),
        "instances": {"primary": states[0], "secondary": states[1]},
        "capturedAppErrors": errors,
    }
except Exception as error:
    results["D09"] = {"outcome": "FAIL", "exception": f"{type(error).__name__}: {error}", "capturedAppErrors": captured(driver)}
finally:
    driver.quit()

time.sleep(0.5)
parts = [path.read_text(encoding="utf-8", errors="replace") if path.exists() else "" for path in PART_LOGS]
combined = "\n".join(parts)
COMBINED_LOG.write_text(combined, encoding="utf-8")
send_lines = [line for line in combined.splitlines() if "sendWithPromise" in line]
js_error_lines = [line for line in combined.splitlines() if "JavaScript error:" in line and "resource://" not in line]
for key in ("D12_loaded_to_loaded", "D12_loading_to_loading"):
    results[key]["sendWithPromiseDriverLogCount"] = sum("sendWithPromise" in line for line in parts[0 if key.endswith("loaded_to_loaded") else 1].splitlines())
    if results[key]["sendWithPromiseDriverLogCount"]:
        results[key]["outcome"] = "FAIL"

payload = {
    "runAtUtc": datetime.now(timezone.utc).isoformat(),
    "browser": capabilities,
    "fixtureManifestHashes": {"normal.pdf": "0aef5927…", "large-linearized.pdf": "abf38a01…"},
    "results": results,
    "summary": {
        "passed": sum(item.get("outcome") == "PASS" for item in results.values()),
        "failed": sum(item.get("outcome") == "FAIL" for item in results.values()),
        "sendWithPromiseCount": len(send_lines),
        "applicationJavaScriptErrorCount": len(js_error_lines),
    },
    "combinedGeckodriverLog": str(COMBINED_LOG.relative_to(ROOT)),
    "partLogs": [str(path.relative_to(ROOT)) for path in PART_LOGS],
    "sendWithPromiseLines": send_lines,
    "applicationJavaScriptErrorLines": js_error_lines,
}
RESULT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
