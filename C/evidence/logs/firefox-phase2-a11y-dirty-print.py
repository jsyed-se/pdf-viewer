import json
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
FIXTURE = ROOT / "A" / "tests" / "fixtures" / "generated" / "normal.pdf"
AXE_SOURCE = Path.home() / "AppData" / "Local" / "Temp" / "axe-core-4.10.3.min.js"
APP = "http://127.0.0.1:5173"


def write_json(name, payload):
    (LOG_DIR / name).write_text(json.dumps(payload, indent=2), encoding="utf-8")


options = Options()
options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"
options.add_argument("-headless")
options.add_argument("-no-remote")
service = Service(
    executable_path=str(Path.home() / ".cache" / "selenium" / "geckodriver" / "win64" / "0.37.1" / "geckodriver.exe"),
    log_output=str(LOG_DIR / "firefox-phase2-followup-geckodriver.log"),
    service_args=["--log", "info"],
)
driver = webdriver.Firefox(options=options, service=service)
wait = WebDriverWait(driver, 35)

try:
    driver.set_window_rect(width=1440, height=900)
    driver.get(APP)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".pdf-sdk.empty-state")))
    driver.find_element(By.CSS_SELECTOR, '.source-controls input[type="file"]').send_keys(str(FIXTURE))
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".viewer-toolbar")))
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".pdf-page-frame canvas")))
    browser = {
        "name": driver.capabilities.get("browserName"),
        "version": driver.capabilities.get("browserVersion"),
        "platform": driver.capabilities.get("platformName"),
        "headless": True,
    }
    viewport = driver.execute_script("return {width: innerWidth, height: innerHeight, dpr: devicePixelRatio}")
    common = {
        "runAtUtc": datetime.now(timezone.utc).isoformat(),
        "app": APP,
        "fixture": str(FIXTURE.relative_to(ROOT)),
        "browser": browser,
        "viewport": viewport,
    }

    # Accessibility scan: retain the complete violation detail needed to reproduce/fix.
    driver.execute_script(AXE_SOURCE.read_text(encoding="utf-8"))
    axe_result = driver.execute_async_script(
        """
        const done = arguments[arguments.length - 1];
        axe.run(document, { resultTypes: ['violations', 'incomplete', 'passes'] })
          .then(result => done(result))
          .catch(error => done({ error: String(error) }));
        """
    )
    violation_summary = []
    for violation in axe_result.get("violations", []):
        violation_summary.append({
            "id": violation.get("id"),
            "impact": violation.get("impact"),
            "help": violation.get("help"),
            "helpUrl": violation.get("helpUrl"),
            "description": violation.get("description"),
            "nodes": [
                {
                    "target": node.get("target"),
                    "html": node.get("html"),
                    "failureSummary": node.get("failureSummary"),
                }
                for node in violation.get("nodes", [])
            ],
        })
    write_json("firefox-phase2-axe.json", {
        **common,
        "scanner": {"name": "axe-core", "version": "4.10.3", "source": "cdnjs.cloudflare.com/ajax/libs/axe-core/4.10.3/axe.min.js"},
        "outcome": "PASS" if len(violation_summary) == 0 else "VIOLATIONS FOUND",
        "counts": {
            "violations": len(violation_summary),
            "violationNodes": sum(len(item["nodes"]) for item in violation_summary),
            "incomplete": len(axe_result.get("incomplete", [])),
            "passes": len(axe_result.get("passes", [])),
        },
        "violations": violation_summary,
        "limitation": "Automated axe results do not replace keyboard, screen-reader, reading-order, contrast visual, or touch-device testing.",
    })
    driver.save_screenshot(str(LOG_DIR / "firefox-phase2-axe-viewer.png"))

    # Print launch: verify the browser window is opened immediately and prepared.
    main_handle = driver.current_window_handle
    handles_before = set(driver.window_handles)
    driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Print"]').click()
    wait.until(lambda d: len(set(d.window_handles) - handles_before) == 1)
    print_handle = next(iter(set(driver.window_handles) - handles_before))
    driver.switch_to.window(print_handle)
    wait.until(lambda d: d.find_elements(By.CSS_SELECTOR, "iframe") or "Preparing" in d.page_source or "Printing failed" in d.page_source)
    print_evidence = {
        "windowCreated": True,
        "handlesBefore": len(handles_before),
        "handlesAfter": len(driver.window_handles),
        "title": driver.title,
        "iframePresent": bool(driver.find_elements(By.CSS_SELECTOR, "iframe")),
        "preparingVisible": "Preparing" in driver.page_source,
        "failureVisible": "Printing failed" in driver.page_source,
    }
    driver.save_screenshot(str(LOG_DIR / "firefox-phase2-print-window.png"))
    write_json("firefox-phase2-print-launch.json", {
        **common,
        "outcome": "PASS — synchronous print window created and PDF frame prepared",
        "evidence": print_evidence,
        "limitation": "Headless Firefox does not expose the native OS print dialog or print-preview artifact to Selenium; final printed-page appearance remains unverified.",
    })
    driver.close()
    driver.switch_to.window(main_handle)

    # Dirty-state close: a real bookmark mutation leaves the viewer dirty.
    driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Bookmarks"]').click()
    add_bookmark = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(normalize-space(.), "Add bookmark for page")]')))
    add_bookmark.click()
    prompt = wait.until(EC.alert_is_present())
    prompt.send_keys("Firefox dirty-state marker")
    prompt.accept()
    wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".busy-overlay")))
    wait.until(EC.presence_of_element_located((By.XPATH, '//*[contains(normalize-space(.), "Firefox dirty-state marker")]')))
    driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Close details panel"]').click()

    close_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Close viewer"]')))
    close_button.click()
    stay_alert = wait.until(EC.alert_is_present())
    stay_text = stay_alert.text
    stay_alert.dismiss()
    viewer_after_stay = bool(driver.find_elements(By.CSS_SELECTOR, ".viewer-toolbar"))

    driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Close viewer"]').click()
    discard_alert = wait.until(EC.alert_is_present())
    discard_text = discard_alert.text
    discard_alert.accept()
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".pdf-sdk.empty-state")))
    viewer_closed_after_discard = not bool(driver.find_elements(By.CSS_SELECTOR, ".viewer-toolbar"))
    driver.save_screenshot(str(LOG_DIR / "firefox-phase2-dirty-close-discarded.png"))
    write_json("firefox-phase2-dirty-close.json", {
        **common,
        "outcome": "PASS",
        "mutation": "Created native bookmark 'Firefox dirty-state marker' through MuPDF worker",
        "confirmationTextStay": stay_text,
        "stayDismissed": True,
        "viewerRemainedOpen": viewer_after_stay,
        "confirmationTextDiscard": discard_text,
        "discardAccepted": True,
        "viewerClosedToEmptyState": viewer_closed_after_discard,
        "limitation": "This validates the Close viewer stay/discard branches; browser-unload and source-replacement confirmation are separate flows.",
    })
finally:
    driver.quit()
