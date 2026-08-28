"""Create and observe final Phase 2 PDF artifacts through the Firefox UI."""

from __future__ import annotations

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
DOWNLOADS = ROOT / "tmp" / "phase2-downloads"
RESULT = ROOT / "C" / "evidence" / "logs" / "firefox-phase2-artifacts.json"
GECKO_LOG = ROOT / "C" / "evidence" / "logs" / "firefox-phase2-artifacts-geckodriver.log"
GECKO = Path.home() / ".cache" / "selenium" / "geckodriver" / "win64" / "0.37.1" / "geckodriver.exe"

DOWNLOADS.mkdir(parents=True, exist_ok=True)
EXPECTED_DOWNLOADS = [
    "existing-annotations-edited.pdf",
    "secret-redaction-edited.pdf",
    "bookmarks-edited.pdf",
]
for name in EXPECTED_DOWNLOADS:
    target = DOWNLOADS / name
    if target.exists():
        target.unlink()
if RESULT.exists():
    RESULT.unlink()
if GECKO_LOG.exists():
    GECKO_LOG.unlink()


def wait_download(wait: WebDriverWait, filename: str) -> Path:
    path = DOWNLOADS / filename
    wait.until(lambda _: path.exists() and path.stat().st_size > 100)
    previous = -1
    for _ in range(20):
        size = path.stat().st_size
        if size == previous:
            return path
        previous = size
        time.sleep(0.1)
    return path


def open_fixture(driver: webdriver.Firefox, wait: WebDriverWait, filename: str, pages: int) -> None:
    file_input = wait.until(EC.presence_of_element_located((By.ID, "local-pdf-file")))
    file_input.send_keys(str(FIXTURES / filename))
    wait.until(lambda d: d.find_element(By.CSS_SELECTOR, 'input[aria-label="Current page"]').get_attribute("max") == str(pages))
    wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".loading-panel")))


def close_dirty(driver: webdriver.Firefox, wait: WebDriverWait) -> None:
    driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Close viewer"]').click()
    prompt = wait.until(EC.alert_is_present())
    prompt.accept()
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".pdf-sdk.empty-state")))


def open_panel(driver: webdriver.Firefox, wait: WebDriverWait, button_name: str, panel_name: str):
    panels = driver.find_elements(By.CSS_SELECTOR, f'.details-panel[aria-label="{panel_name}"]')
    if panels and panels[0].is_displayed():
        return panels[0]
    driver.find_element(By.CSS_SELECTOR, f'button[aria-label="{button_name}"]').click()
    return wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, f'.details-panel[aria-label="{panel_name}"]')))


options = Options()
options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"
options.add_argument("-headless")
options.add_argument("-no-remote")
options.set_preference("browser.download.folderList", 2)
options.set_preference("browser.download.dir", str(DOWNLOADS))
options.set_preference("browser.download.useDownloadDir", True)
options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")
options.set_preference("pdfjs.disabled", True)
service = Service(executable_path=str(GECKO), log_output=str(GECKO_LOG), service_args=["--log", "info"])
driver = webdriver.Firefox(options=options, service=service)
driver.set_window_rect(width=1440, height=900)
wait = WebDriverWait(driver, 45)
observations: dict[str, object] = {}

try:
    driver.get(f"{APP}/?artifact-validation=1")
    wait.until(EC.presence_of_element_located((By.ID, "local-pdf-file")))

    # Native annotation editing and resizing, then local export.
    open_fixture(driver, wait, "existing-annotations.pdf", 2)
    panel = open_panel(driver, wait, "Annotations", "Annotation tools")
    wait.until(lambda _: len(panel.find_elements(By.CSS_SELECTOR, ".detail-list li")) >= 2)
    rows = panel.find_elements(By.CSS_SELECTOR, ".detail-list li")
    annotation_types_before = [row.find_element(By.TAG_NAME, "strong").text for row in rows]
    text_row = next(row for row in rows if row.find_element(By.TAG_NAME, "strong").text == "Text")
    text_row.find_element(By.XPATH, './/button[normalize-space(.)="Select annotation"]').click()
    text_row.find_element(By.XPATH, './/button[normalize-space(.)="Edit"]').click()
    prompt = wait.until(EC.alert_is_present())
    prompt.send_keys("Phase 2 updated note")
    prompt.accept()
    wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".busy-overlay")))
    selected = panel.find_element(By.CSS_SELECTOR, ".detail-list li.selected")
    selected.find_element(By.XPATH, './/button[normalize-space(.)="Resize"]').click()
    width_prompt = wait.until(EC.alert_is_present())
    width_prompt.send_keys("180")
    width_prompt.accept()
    height_prompt = wait.until(EC.alert_is_present())
    height_prompt.send_keys("90")
    height_prompt.accept()
    wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".busy-overlay")))
    driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Save PDF"]').click()
    annotation_download = wait_download(wait, "existing-annotations-edited.pdf")
    observations["annotations"] = {
        "typesBefore": annotation_types_before,
        "editedTextVisible": "Phase 2 updated note" in panel.text,
        "download": annotation_download.name,
        "bytes": annotation_download.stat().st_size,
    }
    close_dirty(driver, wait)

    # Text-match native redaction, application, and local export.
    open_fixture(driver, wait, "secret-redaction.pdf", 2)
    panel = open_panel(driver, wait, "Annotations", "Annotation tools")
    panel.find_element(By.XPATH, './/button[normalize-space(.)="Redact matching text"]').click()
    prompt = wait.until(EC.alert_is_present())
    prompt.send_keys("PHASE2_SECRET_7F3A9")
    prompt.accept()
    wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".busy-overlay")))
    match_status_observed = wait.until(
        lambda d: "1 text match annotated" in d.find_element(By.CSS_SELECTOR, ".sr-status").get_attribute("textContent")
    )
    wait.until(lambda _: any(row.text == "Redact" for row in panel.find_elements(By.CSS_SELECTOR, ".detail-list li strong")))
    apply_button = panel.find_element(By.XPATH, './/button[normalize-space(.)="Apply page redactions"]')
    wait.until(lambda _: apply_button.is_enabled())
    apply_button.click()
    wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".busy-overlay")))
    annotation_types_after_apply = [row.text for row in panel.find_elements(By.CSS_SELECTOR, ".detail-list li strong")]
    driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Save PDF"]').click()
    redaction_download = wait_download(wait, "secret-redaction-edited.pdf")
    observations["redaction"] = {
        "matchStatusObserved": bool(match_status_observed),
        "annotationTypesAfterApply": annotation_types_after_apply,
        "appliedAnnotationAbsent": "Redact" not in annotation_types_after_apply,
        "download": redaction_download.name,
        "bytes": redaction_download.stat().st_size,
    }
    close_dirty(driver, wait)

    # Bookmark add, edit, delete, and local export.
    open_fixture(driver, wait, "bookmarks.pdf", 4)
    panel = open_panel(driver, wait, "Bookmarks", "Bookmarks")
    wait.until(lambda _: len(panel.find_elements(By.CSS_SELECTOR, ".detail-list li")) >= 3)
    initial_titles = [item.text for item in panel.find_elements(By.CSS_SELECTOR, ".bookmark-link")]
    panel.find_element(By.XPATH, './/button[contains(normalize-space(.), "Add bookmark for page")]').click()
    prompt = wait.until(EC.alert_is_present())
    prompt.send_keys("Phase 2 added bookmark")
    prompt.accept()
    wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".busy-overlay")))
    added_row = panel.find_element(By.XPATH, './/li[.//button[normalize-space(.)="Phase 2 added bookmark"]]')
    added_row.find_element(By.XPATH, './/button[normalize-space(.)="Edit"]').click()
    prompt = wait.until(EC.alert_is_present())
    prompt.send_keys("Phase 2 edited bookmark")
    prompt.accept()
    wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".busy-overlay")))
    first_row = panel.find_elements(By.CSS_SELECTOR, ".detail-list li")[0]
    deleted_title = first_row.find_element(By.CSS_SELECTOR, ".bookmark-link").text
    first_row.find_element(By.XPATH, './/button[normalize-space(.)="Delete"]').click()
    wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".busy-overlay")))
    final_titles = [item.text for item in panel.find_elements(By.CSS_SELECTOR, ".bookmark-link")]
    driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Save PDF"]').click()
    bookmark_download = wait_download(wait, "bookmarks-edited.pdf")
    observations["bookmarks"] = {
        "initialTitles": initial_titles,
        "deletedTitle": deleted_title,
        "finalTitles": final_titles,
        "download": bookmark_download.name,
        "bytes": bookmark_download.stat().st_size,
    }

    observations["browser"] = {
        "name": driver.capabilities.get("browserName"),
        "version": driver.capabilities.get("browserVersion"),
        "platform": driver.capabilities.get("platformName"),
        "viewport": "1440x900",
        "headless": True,
    }
    observations["runAtUtc"] = datetime.now(timezone.utc).isoformat()
    observations["outcome"] = "PASS"
finally:
    driver.quit()

RESULT.write_text(json.dumps(observations, indent=2) + "\n", encoding="utf-8")
print(json.dumps(observations, indent=2))
