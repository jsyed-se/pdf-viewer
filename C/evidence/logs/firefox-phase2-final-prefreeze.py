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
SLOW_URL = "http://127.0.0.1:8765/slow-no-range/large-linearized.pdf"
GECKO_LOG = LOG_DIR / "firefox-phase2-final-prefreeze-geckodriver.log"
GECKO_REMAINDER_LOG = LOG_DIR / "firefox-phase2-final-prefreeze-geckodriver-remainder.log"
RESULT_LOG = LOG_DIR / "firefox-phase2-final-prefreeze.json"


def install_capture(driver):
    driver.execute_script(
        """
        window.__prefreezeErrors = [];
        const stringify = value => {
          try { return typeof value === 'string' ? value : JSON.stringify(value); }
          catch (_) { return String(value); }
        };
        const originalError = console.error.bind(console);
        console.error = (...args) => {
          window.__prefreezeErrors.push({kind: 'console.error', message: args.map(stringify).join(' ')});
          originalError(...args);
        };
        window.addEventListener('error', event => window.__prefreezeErrors.push({kind: 'window.error', message: event.message || String(event.error)}));
        window.addEventListener('unhandledrejection', event => window.__prefreezeErrors.push({kind: 'unhandledrejection', message: stringify(event.reason)}));
        """
    )


def captured(driver):
    return driver.execute_script("return window.__prefreezeErrors || []")


def open_local(driver, name):
    WebDriverWait(driver, 40).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '.source-controls input[type="file"]'))
    ).send_keys(str(FIXTURES / name))


if GECKO_LOG.exists():
    GECKO_LOG.unlink()
if GECKO_REMAINDER_LOG.exists():
    GECKO_REMAINDER_LOG.unlink()
if RESULT_LOG.exists():
    RESULT_LOG.unlink()

options = Options()
options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"
options.add_argument("-headless")
options.add_argument("-no-remote")
service = Service(
    executable_path=str(Path.home() / ".cache" / "selenium" / "geckodriver" / "win64" / "0.37.1" / "geckodriver.exe"),
    log_output=str(GECKO_LOG),
    service_args=["--log", "info"],
)
driver = webdriver.Firefox(options=options, service=service)
wait = WebDriverWait(driver, 40)
results = {}

try:
    driver.set_window_rect(width=1440, height=900)
    browser = {
        "name": driver.capabilities.get("browserName"),
        "version": driver.capabilities.get("browserVersion"),
        "platform": driver.capabilities.get("platformName"),
        "headless": True,
    }

    # D11: slow no-range cancellation.
    driver.get(APP)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".pdf-sdk.empty-state")))
    install_capture(driver)
    url_input = driver.find_element(By.CSS_SELECTOR, 'input[aria-label="Remote PDF URL"]')
    url_input.send_keys(SLOW_URL)
    started = time.perf_counter()
    driver.find_element(By.CSS_SELECTOR, '.source-controls button[type="submit"]').click()
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".loading-panel")))
    progress_seen = False
    try:
        WebDriverWait(driver, 8).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".loading-panel progress")))
        progress_seen = True
    except Exception:
        progress_seen = False
    cancel_started = time.perf_counter()
    driver.find_element(By.XPATH, '//button[normalize-space(.)="Cancel loading"]').click()
    wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".loading-panel")))
    cancel_latency_ms = round((time.perf_counter() - cancel_started) * 1000, 1)
    status_after_cancel = driver.find_element(By.CSS_SELECTOR, ".sr-status").text or driver.find_element(By.CSS_SELECTOR, ".sr-status").get_attribute("textContent")
    time.sleep(4.0)
    d11_errors = captured(driver)
    d11_toolbar_absent = not bool(driver.find_elements(By.CSS_SELECTOR, ".viewer-toolbar"))
    d11_error_absent = not bool(driver.find_elements(By.CSS_SELECTOR, ".error-banner"))
    d11_pass = status_after_cancel.strip() == "Loading cancelled." and d11_toolbar_absent and d11_error_absent
    results["D11"] = {
        "outcome": "PASS" if d11_pass else "FAIL",
        "url": SLOW_URL,
        "progressSeen": progress_seen,
        "cancelLatencyMs": cancel_latency_ms,
        "elapsedFromSubmitMs": round((time.perf_counter() - started) * 1000, 1),
        "status": status_after_cancel.strip(),
        "loadingControlsRemoved": not bool(driver.find_elements(By.CSS_SELECTOR, ".loading-panel")),
        "documentNotInstalledAfter4s": d11_toolbar_absent,
        "errorBannerAbsent": d11_error_absent,
        "capturedPageErrors": d11_errors,
    }

    # Isolate the intentionally aborted network task from subsequent source tests.
    driver.quit()
    d11_gecko_text = GECKO_LOG.read_text(encoding="utf-8", errors="replace")
    service = Service(
        executable_path=str(Path.home() / ".cache" / "selenium" / "geckodriver" / "win64" / "0.37.1" / "geckodriver.exe"),
        log_output=str(GECKO_REMAINDER_LOG),
        service_args=["--log", "info"],
    )
    driver = webdriver.Firefox(options=options, service=service)
    driver.set_window_rect(width=1440, height=900)
    wait = WebDriverWait(driver, 40)

    # D12: repeatedly replace active local PDFs while canvas/text work is live.
    driver.get(f"{APP}/?prefreeze=d12")
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".source-controls")))
    replacement_sequence = ["normal.pdf", "multi-page-text.pdf", "existing-annotations.pdf", "normal.pdf", "multi-page-text.pdf"]
    completed_replacements = []
    try:
        open_local(driver, "normal.pdf")
        completed_replacements.append("normal.pdf")
        wait.until(lambda d: d.find_element(By.CSS_SELECTOR, 'input[aria-label="Current page"]').get_attribute("max") == "2")
        install_capture(driver)
        open_local(driver, "multi-page-text.pdf")
        completed_replacements.append("multi-page-text.pdf")
        wait.until(lambda d: d.find_element(By.CSS_SELECTOR, 'input[aria-label="Current page"]').get_attribute("max") == "16")
        workspace = driver.find_element(By.CSS_SELECTOR, ".page-workspace")
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", workspace)
        time.sleep(0.15)
        for name in replacement_sequence[2:]:
            open_local(driver, name)
            completed_replacements.append(name)
            time.sleep(0.15)
        wait.until(lambda d: d.find_element(By.CSS_SELECTOR, 'input[aria-label="Current page"]').get_attribute("max") == "16")
        time.sleep(3.0)
        d12_errors = captured(driver)
        d12_page = driver.find_element(By.CSS_SELECTOR, 'input[aria-label="Current page"]').get_attribute("value")
        d12_ready = driver.find_element(By.CSS_SELECTOR, ".attachment-summary small").text
        d12_exception = None
    except Exception as error:
        d12_exception = f"{type(error).__name__}: {error}".strip()
        try:
            d12_errors = captured(driver)
        except Exception:
            d12_errors = []
        page_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[aria-label="Current page"]')
        d12_page = page_inputs[0].get_attribute("value") if page_inputs else None
        summaries = driver.find_elements(By.CSS_SELECTOR, ".attachment-summary small")
        d12_ready = summaries[0].text if summaries else None
    d12_send_errors_page = [item for item in d12_errors if "sendWithPromise" in item.get("message", "")]
    results["D12"] = {
        "outcome": "PASS" if not d12_exception and d12_page == "1" and d12_ready and "16 pages ready" in d12_ready and not d12_send_errors_page else "FAIL",
        "replacementSequence": replacement_sequence,
        "completedReplacementInputs": completed_replacements,
        "finalPageCount": 16 if d12_ready and "16 pages ready" in d12_ready else None,
        "finalCurrentPage": d12_page,
        "hostStatus": d12_ready,
        "runnerObservedException": d12_exception,
        "capturedPageErrors": d12_errors,
        "capturedSendWithPromiseErrors": d12_send_errors_page,
    }

    # D09: dual raw-byte harness, callback ordering, and instance isolation.
    driver.get(f"{APP}/tests/harness.html?dual=1")
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".sdk-host")))
    wait.until(lambda d: "primary:ready:normal.pdf:2" in d.find_element(By.CSS_SELECTOR, ".harness-log output").text)
    wait.until(lambda d: "secondary:ready:merge-beta.pdf:2" in d.find_element(By.CSS_SELECTOR, ".harness-log output").text)
    install_capture(driver)
    time.sleep(1.5)
    before_lines = driver.find_element(By.CSS_SELECTOR, ".harness-log output").text.splitlines()
    driver.find_element(By.XPATH, '//button[normalize-space(.)="Replace primary bytes"]').click()
    wait.until(lambda d: "primary:ready:multi-page-text.pdf:16" in d.find_element(By.CSS_SELECTOR, ".harness-log output").text)
    time.sleep(3.0)
    after_lines = driver.find_element(By.CSS_SELECTOR, ".harness-log output").text.splitlines()
    delta = after_lines[len(before_lines):]
    hosts = driver.find_elements(By.CSS_SELECTOR, ".sdk-host")
    primary_max = hosts[0].find_element(By.CSS_SELECTOR, 'input[aria-label="Current page"]').get_attribute("max")
    primary_page = hosts[0].find_element(By.CSS_SELECTOR, 'input[aria-label="Current page"]').get_attribute("value")
    secondary_max = hosts[1].find_element(By.CSS_SELECTOR, 'input[aria-label="Current page"]').get_attribute("max")
    secondary_page = hosts[1].find_element(By.CSS_SELECTOR, 'input[aria-label="Current page"]').get_attribute("value")
    d09_errors = captured(driver)
    d09_page_callbacks = [line for line in delta if line.startswith("primary:page:")]
    d09_secondary_events = [line for line in delta if line.startswith("secondary:")]
    d09_pass = (
        "primary:ready:multi-page-text.pdf:16" in delta
        and not d09_page_callbacks
        and not d09_secondary_events
        and primary_max == "16"
        and primary_page == "1"
        and secondary_max == "2"
        and secondary_page == "1"
    )
    results["D09"] = {
        "outcome": "PASS" if d09_pass else "FAIL",
        "eventsBeforeReplacement": before_lines,
        "eventsAfterReplacement": delta,
        "spuriousPrimaryPageCallbacks": d09_page_callbacks,
        "secondaryEventsDuringPrimaryReplacement": d09_secondary_events,
        "primary": {"pageCount": int(primary_max), "currentPage": int(primary_page)},
        "secondary": {"pageCount": int(secondary_max), "currentPage": int(secondary_page)},
        "capturedPageErrors": d09_errors,
    }
finally:
    driver.quit()

time.sleep(0.5)
remainder_gecko_text = GECKO_REMAINDER_LOG.read_text(encoding="utf-8", errors="replace") if GECKO_REMAINDER_LOG.exists() else ""
gecko_text = d11_gecko_text + "\n" + remainder_gecko_text
GECKO_LOG.write_text(gecko_text, encoding="utf-8")
send_lines = [line for line in gecko_text.splitlines() if "sendWithPromise" in line]
payload = {
    "runAtUtc": datetime.now(timezone.utc).isoformat(),
    "browser": browser,
    "fixtureManifestHashes": {
        "normal.pdf": "0aef5927…",
        "large-linearized.pdf": "abf38a01…",
    },
    "results": results,
    "geckodriverLog": str(GECKO_LOG.relative_to(ROOT)),
    "sendWithPromise": {
        "occurred": bool(send_lines),
        "count": len(send_lines),
        "lines": send_lines,
    },
    "limitations": [
        "Headless Firefox validation does not replace manual screen-reader, touch, native print, or broad visual certification.",
        "The repeated replacement sequence is deterministic stress evidence, not an exhaustive scheduler/race proof.",
    ],
}
RESULT_LOG.write_text(json.dumps(payload, indent=2), encoding="utf-8")
