import json
import time
from datetime import datetime, timezone
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait


ROOT = Path(__file__).resolve().parents[3]
LOG_DIR = ROOT / "C" / "evidence" / "logs"
FIXTURES = ROOT / "A" / "tests" / "fixtures" / "generated"
AXE_SOURCE = Path.home() / "AppData" / "Local" / "Temp" / "axe-core-4.10.3.min.js"
APP = "http://127.0.0.1:5173"


def check(name, outcome, details, evidence=None):
    item = {"name": name, "outcome": outcome, "details": details}
    if evidence is not None:
        item["evidence"] = evidence
    return item


def open_fixture(driver, wait, filename, expected_pages=None):
    file_input = driver.find_element(By.CSS_SELECTOR, '.source-controls input[type="file"]')
    file_input.send_keys(str(FIXTURES / filename))
    if expected_pages is None:
        return
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".viewer-toolbar")))
    wait.until(lambda d: d.find_element(By.CSS_SELECTOR, 'input[aria-label="Current page"]').get_attribute("max") == str(expected_pages))


options = Options()
options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"
options.add_argument("-headless")
options.add_argument("-no-remote")
service = Service(
    executable_path=str(Path.home() / ".cache" / "selenium" / "geckodriver" / "win64" / "0.37.1" / "geckodriver.exe"),
    log_output=str(LOG_DIR / "firefox-phase2-revalidation-geckodriver.log"),
    service_args=["--log", "info"],
)
driver = webdriver.Firefox(options=options, service=service)
wait = WebDriverWait(driver, 35)
results = []

try:
    driver.set_window_rect(width=1440, height=900)
    driver.get(APP)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".pdf-sdk.empty-state")))
    browser = {
        "name": driver.capabilities.get("browserName"),
        "version": driver.capabilities.get("browserVersion"),
        "platform": driver.capabilities.get("platformName"),
        "headless": True,
    }
    desktop_viewport = driver.execute_script("return {width: innerWidth, height: innerHeight, dpr: devicePixelRatio}")

    # Principal workflow: local load, navigation, modes, zoom/fit, editor operation.
    open_fixture(driver, wait, "normal.pdf", 2)
    results.append(check("Principal/local fixture", "PASS", "normal.pdf loaded with 2 pages in the viewer."))

    driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Next page"]').click()
    wait.until(lambda d: d.find_element(By.CSS_SELECTOR, 'input[aria-label="Current page"]').get_attribute("value") == "2")
    driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Previous page"]').click()
    wait.until(lambda d: d.find_element(By.CSS_SELECTOR, 'input[aria-label="Current page"]').get_attribute("value") == "1")
    modes = Select(driver.find_element(By.CSS_SELECTOR, 'select[aria-label="Scroll mode"]'))
    for value in ("single", "spread", "continuous"):
        modes.select_by_value(value)
    zoom_before = driver.find_element(By.CSS_SELECTOR, ".zoom-value").text
    driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Zoom in"]').click()
    wait.until(lambda d: d.find_element(By.CSS_SELECTOR, ".zoom-value").text != zoom_before)
    zoom_after = driver.find_element(By.CSS_SELECTOR, ".zoom-value").text
    driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Fit width"]').click()
    driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Fit viewport"]').click()
    results.append(check("Principal/navigation, modes, zoom", "PASS", f"Previous/next passed; selected single/spread/continuous; zoom changed {zoom_before}→{zoom_after}; both fit controls activated."))

    driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Edit document"]').click()
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".document-editor")))
    driver.find_elements(By.CSS_SELECTOR, ".page-select-button")[0].click()
    driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Rotate right"]').click()
    wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".busy-overlay")))
    wait.until(lambda d: "90°" in d.find_elements(By.CSS_SELECTOR, ".reorder-row span")[0].text)
    driver.find_element(By.XPATH, '//button[contains(normalize-space(.), "Save changes")]').click()
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".viewer-toolbar")))
    results.append(check("Principal/editor real operation", "PASS", "Selected page 1, serialized a 90° right rotation through the editor, and saved to the viewer."))
    driver.save_screenshot(str(LOG_DIR / "firefox-phase2-revalidation-principal.png"))

    # Current page direct-navigation and real-scroll stability.
    page_input = driver.find_element(By.CSS_SELECTOR, 'input[aria-label="Current page"]')
    page_input.clear()
    page_input.send_keys("2\ue007")
    wait.until(lambda d: d.find_element(By.CSS_SELECTOR, 'input[aria-label="Current page"]').get_attribute("value") == "2")
    time.sleep(2.0)
    direct_stable = driver.find_element(By.CSS_SELECTOR, 'input[aria-label="Current page"]').get_attribute("value") == "2"
    workspace = driver.find_element(By.CSS_SELECTOR, ".page-workspace")
    driver.execute_script("arguments[0].scrollTop = 0", workspace)
    wait.until(lambda d: d.find_element(By.CSS_SELECTOR, 'input[aria-label="Current page"]').get_attribute("value") == "1")
    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", workspace)
    wait.until(lambda d: d.find_element(By.CSS_SELECTOR, 'input[aria-label="Current page"]').get_attribute("value") == "2")
    time.sleep(2.0)
    scroll_stable = driver.find_element(By.CSS_SELECTOR, 'input[aria-label="Current page"]').get_attribute("value") == "2"
    results.append(check("Current-page tracking stability", "PASS" if direct_stable and scroll_stable else "FAIL", "Direct page 2 remained stable for 2 seconds; real workspace scroll tracked page 1 then page 2 and remained stable for 2 seconds.", {"directStable": direct_stable, "scrollStable": scroll_stable}))

    # D07: existing Text and Highlight annotations must initialize/list in Firefox.
    driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Close viewer"]').click()
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".pdf-sdk.empty-state")))
    open_fixture(driver, wait, "existing-annotations.pdf", 2)
    driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Annotations"]').click()
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.details-panel[aria-label="Annotation tools"]')))
    wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".busy-overlay")))
    wait.until(lambda d: len(d.find_elements(By.CSS_SELECTOR, ".detail-list li strong")) >= 2)
    annotation_types = [element.text for element in driver.find_elements(By.CSS_SELECTOR, ".detail-list li strong")]
    d07_pass = "Text" in annotation_types and "Highlight" in annotation_types
    results.append(check("P2-D07 existing annotations", "PASS" if d07_pass else "FAIL", "Annotations panel initialized MuPDF metadata and listed existing annotation types.", annotation_types))
    driver.save_screenshot(str(LOG_DIR / "firefox-phase2-revalidation-d07-annotations.png"))
    driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Close details panel"]').click()

    # D09: same-instance source replacement and settling stability. The demo does not expose callback logs.
    open_fixture(driver, wait, "multi-page-text.pdf", 16)
    replacement_page = driver.find_element(By.CSS_SELECTOR, 'input[aria-label="Current page"]').get_attribute("value")
    time.sleep(3.0)
    replacement_stable = driver.find_element(By.CSS_SELECTOR, 'input[aria-label="Current page"]').get_attribute("value") == "1"
    host_ready = "16 pages ready" in driver.find_element(By.CSS_SELECTOR, ".attachment-summary small").text
    results.append(check("P2-D09 source replacement/scroll stability", "PARTIAL" if replacement_stable and host_ready else "FAIL", "Firefox replacement changed the same SDK instance from 2 to 16 pages, settled at page 1 for 3 seconds, and rendered the new host-ready state. The demo has no callback event log or dual-instance raw-byte harness, so absence/order of onPageChange callbacks is not directly proven.", {"initialPageAfterReplacement": replacement_page, "stableAtPage1": replacement_stable, "hostReady": host_ready, "callbackHarnessAvailable": False}))
    driver.save_screenshot(str(LOG_DIR / "firefox-phase2-revalidation-d09-replacement.png"))

    # D08: unsupported local bytes must give accurate guidance and no viewer workspace.
    driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Close viewer"]').click()
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".pdf-sdk.empty-state")))
    driver.find_element(By.CSS_SELECTOR, '.source-controls input[type="file"]').send_keys(str(LOG_DIR / "firefox-phase2-revalidation-unsupported.pdf"))
    error_banner = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".error-banner")))
    error_text = error_banner.text
    host_error = driver.find_element(By.CSS_SELECTOR, ".attachment-summary small").text
    workspace_absent = not bool(driver.find_elements(By.CSS_SELECTOR, ".viewer-toolbar"))
    d08_pass = "not a valid or supported PDF" in error_text and "not a valid or supported PDF" in host_error and workspace_absent
    results.append(check("P2-D08 unsupported-file guidance", "PASS" if d08_pass else "FAIL", "Unsupported plain-text fixture was rejected with invalid/supported-PDF guidance in both viewer alert and host callback state; no PDF workspace rendered.", {"errorBanner": error_text, "hostError": host_error, "workspaceAbsent": workspace_absent}))
    driver.save_screenshot(str(LOG_DIR / "firefox-phase2-revalidation-d08-unsupported.png"))

    # Reload representative normal viewer for corrected D10 axe scan.
    open_fixture(driver, wait, "normal.pdf", 2)
    driver.execute_script(AXE_SOURCE.read_text(encoding="utf-8"))
    axe_result = driver.execute_async_script(
        """
        const done = arguments[arguments.length - 1];
        axe.run(document, { resultTypes: ['violations', 'incomplete', 'passes'] })
          .then(result => done(result))
          .catch(error => done({ error: String(error) }));
        """
    )
    violations = []
    for violation in axe_result.get("violations", []):
        violations.append({
            "id": violation.get("id"),
            "impact": violation.get("impact"),
            "help": violation.get("help"),
            "helpUrl": violation.get("helpUrl"),
            "nodes": [{"target": n.get("target"), "html": n.get("html"), "failureSummary": n.get("failureSummary")} for n in violation.get("nodes", [])],
        })
    axe_payload = {
        "runAtUtc": datetime.now(timezone.utc).isoformat(),
        "browser": browser,
        "viewport": desktop_viewport,
        "fixture": "A/tests/fixtures/generated/normal.pdf",
        "scanner": {"name": "axe-core", "version": "4.10.3"},
        "outcome": "PASS" if not violations else "VIOLATIONS FOUND",
        "counts": {"violations": len(violations), "violationNodes": sum(len(v["nodes"]) for v in violations), "incomplete": len(axe_result.get("incomplete", [])), "passes": len(axe_result.get("passes", []))},
        "violations": violations,
        "limitation": "Automated axe does not replace keyboard, screen-reader, reading-order, visual contrast, or touch validation.",
    }
    (LOG_DIR / "firefox-phase2-revalidation-axe.json").write_text(json.dumps(axe_payload, indent=2), encoding="utf-8")
    results.append(check("P2-D10 axe-core revalidation", "PASS" if not violations else "FAIL", f"axe-core 4.10.3 returned {len(violations)} violation rules and {axe_payload['counts']['violationNodes']} affected nodes.", axe_payload["counts"]))
    driver.save_screenshot(str(LOG_DIR / "firefox-phase2-revalidation-axe.png"))

    # Principal responsive rerun.
    driver.set_window_rect(width=820, height=980)
    time.sleep(1.0)
    responsive = driver.execute_script("return {width: innerWidth, height: innerHeight, bodyScrollWidth: document.body.scrollWidth, dpr: devicePixelRatio}")
    toolbar = driver.find_element(By.CSS_SELECTOR, ".viewer-toolbar")
    toolbar_metrics = driver.execute_script("return {clientWidth: arguments[0].clientWidth, scrollWidth: arguments[0].scrollWidth, overflowX: getComputedStyle(arguments[0]).overflowX}", toolbar)
    responsive_pass = responsive["bodyScrollWidth"] <= responsive["width"] and toolbar_metrics["overflowX"] in ("auto", "scroll")
    results.append(check("Principal/responsive layout", "PASS" if responsive_pass else "FAIL", "Responsive viewport retained page width and keyboard-scrollable toolbar overflow.", {"viewport": responsive, "toolbar": toolbar_metrics}))
    driver.save_screenshot(str(LOG_DIR / "firefox-phase2-revalidation-responsive.png"))

    payload = {
        "runAtUtc": datetime.now(timezone.utc).isoformat(),
        "app": APP,
        "browser": browser,
        "desktopViewport": desktop_viewport,
        "results": results,
        "limitations": [
            "The demo does not expose onPageChange callback logs or the Chromium dual-instance raw-byte harness; D09 callback-sequence proof remains partial in Firefox.",
            "Headless automation validates DOM/browser behavior and screenshots, not screen-reader, real touch, native print, or broad compatibility certification.",
        ],
    }
    (LOG_DIR / "firefox-phase2-revalidation.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
finally:
    driver.quit()
