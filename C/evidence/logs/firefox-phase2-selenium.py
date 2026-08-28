import json
import time
from datetime import datetime, timezone
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait


ROOT = Path(__file__).resolve().parents[3]
FIXTURE = ROOT / "A" / "tests" / "fixtures" / "generated" / "normal.pdf"
LOG = ROOT / "C" / "evidence" / "logs" / "firefox-phase2-principal-workflow.json"
SCREEN_PREFIX = ROOT / "C" / "evidence" / "logs" / "firefox-phase2"
APP = "http://127.0.0.1:5173"


def result(name, outcome, details, evidence=None):
    record = {"name": name, "outcome": outcome, "details": details}
    if evidence:
        record["evidence"] = evidence
    return record


options = Options()
options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"
options.add_argument("-headless")
options.add_argument("-no-remote")
service = Service(
    executable_path=str(Path.home() / ".cache" / "selenium" / "geckodriver" / "win64" / "0.37.1" / "geckodriver.exe"),
    log_output=str(ROOT / "C" / "evidence" / "logs" / "firefox-phase2-geckodriver.log"),
    service_args=["--log", "debug"],
)
driver = webdriver.Firefox(options=options, service=service)
wait = WebDriverWait(driver, 35)
records = []

try:
    driver.set_window_rect(width=1440, height=900)
    driver.get(APP)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".pdf-sdk.empty-state")))
    desktop_viewport = driver.execute_script("return {width: innerWidth, height: innerHeight, dpr: devicePixelRatio}")

    file_input = driver.find_element(By.CSS_SELECTOR, '.source-controls input[type="file"]')
    file_input.send_keys(str(FIXTURE))
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".viewer-toolbar")))
    wait.until(lambda d: int(d.find_element(By.CSS_SELECTOR, 'input[aria-label="Current page"]').get_attribute("max")) > 0)
    page_input = driver.find_element(By.CSS_SELECTOR, 'input[aria-label="Current page"]')
    page_count = int(page_input.get_attribute("max"))
    records.append(result("Local fixture loading", "PASS", f"Loaded normal.pdf with {page_count} pages; viewer toolbar became available."))
    driver.save_screenshot(str(SCREEN_PREFIX) + "-loaded.png")

    driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Next page"]').click()
    wait.until(lambda d: d.find_element(By.CSS_SELECTOR, 'input[aria-label="Current page"]').get_attribute("value") == "2")
    next_value = driver.find_element(By.CSS_SELECTOR, 'input[aria-label="Current page"]').get_attribute("value")
    driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Previous page"]').click()
    wait.until(lambda d: d.find_element(By.CSS_SELECTOR, 'input[aria-label="Current page"]').get_attribute("value") == "1")
    direct = driver.find_element(By.CSS_SELECTOR, 'input[aria-label="Current page"]')
    direct.clear()
    direct.send_keys(str(page_count))
    direct.send_keys("\ue007")
    wait.until(lambda d: d.find_element(By.CSS_SELECTOR, 'input[aria-label="Current page"]').get_attribute("value") == str(page_count))
    records.append(result("Page navigation", "PASS", f"Next reached page {next_value}; previous returned to 1; direct navigation reached {page_count}."))

    mode = Select(driver.find_element(By.CSS_SELECTOR, 'select[aria-label="Scroll mode"]'))
    observed_modes = []
    for value in ("single", "spread", "continuous"):
        mode.select_by_value(value)
        wait.until(lambda d, v=value: d.find_element(By.CSS_SELECTOR, 'select[aria-label="Scroll mode"]').get_attribute("value") == v)
        observed_modes.append(value)
    records.append(result("View modes", "PASS", "Selected single, spread, and continuous modes successfully.", observed_modes))

    zoom_before = driver.find_element(By.CSS_SELECTOR, ".zoom-value").text
    driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Zoom in"]').click()
    wait.until(lambda d: d.find_element(By.CSS_SELECTOR, ".zoom-value").text != zoom_before)
    zoom_in = driver.find_element(By.CSS_SELECTOR, ".zoom-value").text
    driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Zoom out"]').click()
    driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Fit width"]').click()
    fit_width_pressed = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Fit width"]').get_attribute("aria-pressed")
    driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Fit viewport"]').click()
    fit_viewport_pressed = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Fit viewport"]').get_attribute("aria-pressed")
    records.append(result("Zoom and fit controls", "PASS", f"Zoom changed {zoom_before} → {zoom_in}; fit-width pressed={fit_width_pressed}; fit-viewport pressed={fit_viewport_pressed}."))

    driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Annotations"]').click()
    panel = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.details-panel[aria-label="Annotation tools"]')))
    annotation_actions = [item.text for item in panel.find_elements(By.CSS_SELECTOR, ".panel-action-grid button")]
    blocker = panel.find_element(By.CSS_SELECTOR, ".capability-note").text
    records.append(result("Annotations panel", "PASS", "Annotation actions and honest signature blocker were visible.", {"actions": annotation_actions, "blocker": blocker}))

    driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Close details panel"]').click()
    driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Edit document"]').click()
    editor = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".document-editor")))
    first_select = editor.find_elements(By.CSS_SELECTOR, ".page-select-button")[0]
    first_select.click()
    wait.until(lambda d: d.find_elements(By.CSS_SELECTOR, ".editor-page-card.selected"))
    driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Rotate right"]').click()
    wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".busy-overlay")))
    wait.until(lambda d: "90°" in d.find_elements(By.CSS_SELECTOR, ".reorder-row span")[0].text)
    rotation_text = driver.find_elements(By.CSS_SELECTOR, ".reorder-row span")[0].text
    driver.save_screenshot(str(SCREEN_PREFIX) + "-editor-rotated.png")
    driver.find_element(By.XPATH, '//button[contains(normalize-space(.), "Save changes")]').click()
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".viewer-toolbar")))
    records.append(result("Editor entry and real operation", "PASS", f"Entered MuPDF editor, selected page 1, serialized right rotation ({rotation_text}), and saved back to viewer."))

    driver.set_window_rect(width=820, height=980)
    time.sleep(1.0)
    tablet_viewport = driver.execute_script("return {width: innerWidth, height: innerHeight, dpr: devicePixelRatio, bodyScrollWidth: document.body.scrollWidth}")
    toolbar = driver.find_element(By.CSS_SELECTOR, ".viewer-toolbar")
    toolbar_metrics = driver.execute_script("return {clientWidth: arguments[0].clientWidth, scrollWidth: arguments[0].scrollWidth, overflowX: getComputedStyle(arguments[0]).overflowX}", toolbar)
    source_controls_display = driver.execute_script("return getComputedStyle(document.querySelector('.source-controls')).display")
    responsive_ok = tablet_viewport["bodyScrollWidth"] <= tablet_viewport["width"] and toolbar_metrics["overflowX"] in ("auto", "scroll")
    records.append(result("Responsive tablet layout", "PASS" if responsive_ok else "FAIL", f"Viewport {tablet_viewport['width']}×{tablet_viewport['height']}; body scroll width {tablet_viewport['bodyScrollWidth']}; toolbar overflow {toolbar_metrics}; source controls display={source_controls_display}."))
    driver.save_screenshot(str(SCREEN_PREFIX) + "-responsive.png")

    payload = {
        "runAtUtc": datetime.now(timezone.utc).isoformat(),
        "app": APP,
        "fixture": str(FIXTURE.relative_to(ROOT)),
        "browser": {
            "name": driver.capabilities.get("browserName"),
            "version": driver.capabilities.get("browserVersion"),
            "platform": driver.capabilities.get("platformName"),
            "headless": True,
        },
        "viewports": {"desktop": desktop_viewport, "tablet": tablet_viewport},
        "results": records,
        "limitations": [
            "Headless Selenium validates DOM, browser execution, and screenshots but is not a screen-reader or touch-device certification.",
            "Only one real editor mutation (page rotation and save) was required and exercised in this principal workflow.",
            "Print UI, downloads/reopen, password/error paths, annotation creation, and broad Firefox certification are outside this focused run.",
        ],
    }
    LOG.write_text(json.dumps(payload, indent=2), encoding="utf-8")
finally:
    driver.quit()
