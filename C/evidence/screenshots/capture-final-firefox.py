"""Capture the concise final Phase 2 UI evidence set from the frozen app commit."""

from __future__ import annotations

import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait


ROOT = Path(__file__).resolve().parents[3]
APP = "http://127.0.0.1:5173"
FIXTURES = ROOT / "A" / "tests" / "fixtures" / "generated"
ARTIFACTS = ROOT / "C" / "evidence" / "generated-pdfs"
OUTPUT = ROOT / "C" / "evidence" / "screenshots"
GECKO = Path.home() / ".cache" / "selenium" / "geckodriver" / "win64" / "0.37.1" / "geckodriver.exe"
COMMIT = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def open_pdf(driver: webdriver.Firefox, wait: WebDriverWait, path: Path, pages: int) -> None:
    wait.until(EC.presence_of_element_located((By.ID, "local-pdf-file"))).send_keys(str(path))
    wait.until(lambda d: d.find_element(By.CSS_SELECTOR, 'input[aria-label="Current page"]').get_attribute("max") == str(pages))
    wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".loading-panel")))


def shot(driver: webdriver.Firefox, name: str, records: list[dict[str, object]], purpose: str) -> None:
    path = OUTPUT / name
    driver.save_screenshot(str(path))
    records.append({"filename": name, "purpose": purpose, "bytes": path.stat().st_size})


options = Options()
options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"
options.add_argument("-headless")
options.add_argument("-no-remote")
service = Service(executable_path=str(GECKO), log_output=str(OUTPUT / "final-firefox-geckodriver.log"))
driver = webdriver.Firefox(options=options, service=service)
driver.set_window_rect(width=1440, height=900)
wait = WebDriverWait(driver, 45)
records: list[dict[str, object]] = []

try:
    driver.get(f"{APP}/?evidence=final-{COMMIT[:7]}")
    open_pdf(driver, wait, FIXTURES / "normal.pdf", 2)
    shot(driver, "01-firefox-desktop-continuous.png", records, "Host/SDK boundary, thumbnails, corrected fixture spacing, and continuous mode")

    modes = Select(driver.find_element(By.CSS_SELECTOR, 'select[aria-label="Scroll mode"]'))
    modes.select_by_value("single")
    wait.until(lambda d: len(d.find_elements(By.CSS_SELECTOR, ".page-workspace .pdf-page-frame")) == 1)
    time.sleep(0.4)
    shot(driver, "02-firefox-single-page.png", records, "Single-page mode and centered page presentation")

    driver.get(f"{APP}/?evidence=spread-{COMMIT[:7]}")
    open_pdf(driver, wait, FIXTURES / "multi-page-text.pdf", 16)
    driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Next page"]').click()
    wait.until(lambda d: d.find_element(By.CSS_SELECTOR, 'input[aria-label="Current page"]').get_attribute("value") == "2")
    modes = Select(driver.find_element(By.CSS_SELECTOR, 'select[aria-label="Scroll mode"]'))
    modes.select_by_value("spread")
    wait.until(lambda d: len(d.find_elements(By.CSS_SELECTOR, ".page-workspace .pdf-page-frame")) == 2)
    driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Fit viewport"]').click()
    wait.until(lambda d: d.find_element(By.CSS_SELECTOR, 'button[aria-label="Fit viewport"]').get_attribute("aria-pressed") == "true")
    time.sleep(0.4)
    shot(driver, "03-firefox-spread.png", records, "Per-spread mode with two pages")

    driver.get(f"{APP}/?evidence=editor-{COMMIT[:7]}")
    open_pdf(driver, wait, FIXTURES / "merge-alpha.pdf", 3)
    driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Edit document"]').click()
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".document-editor")))
    driver.find_elements(By.CSS_SELECTOR, ".page-select-button")[0].click()
    driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Rotate right"]').click()
    wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".busy-overlay")))
    wait.until(lambda d: "90°" in d.find_elements(By.CSS_SELECTOR, ".reorder-row span")[0].text)
    shot(driver, "04-firefox-editor-page-organization.png", records, "Editor selection, page organization, rotation, and manipulation toolbar")

    driver.get(f"{APP}/?evidence=annotations-{COMMIT[:7]}")
    open_pdf(driver, wait, ARTIFACTS / "existing-annotations-edited.pdf", 2)
    driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Annotations"]').click()
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.details-panel[aria-label="Annotation tools"]')))
    wait.until(lambda d: len(d.find_elements(By.CSS_SELECTOR, ".detail-list li")) >= 2)
    shot(driver, "05-firefox-native-annotations.png", records, "Native Text/Highlight inspection and edited note persistence")

    driver.get(f"{APP}/?evidence=bookmarks-{COMMIT[:7]}")
    open_pdf(driver, wait, ARTIFACTS / "bookmarks-edited.pdf", 4)
    driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Bookmarks"]').click()
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.details-panel[aria-label="Bookmarks"]')))
    wait.until(EC.presence_of_element_located((By.XPATH, '//*[contains(normalize-space(.), "Phase 2 edited bookmark")]')))
    shot(driver, "06-firefox-bookmark-management.png", records, "Persisted native bookmark edit and bookmark controls")

    driver.get(f"{APP}/?evidence=redaction-{COMMIT[:7]}")
    open_pdf(driver, wait, ARTIFACTS / "applied-redaction.pdf", 2)
    shot(driver, "07-firefox-applied-redaction.png", records, "Reopened applied-redaction output with the secret visibly removed")

    driver.get(f"{APP}/?evidence=error-{COMMIT[:7]}")
    wait.until(EC.presence_of_element_located((By.ID, "local-pdf-file"))).send_keys(str(FIXTURES / "unsupported.txt"))
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".error-banner")))
    shot(driver, "08-firefox-error-guidance.png", records, "Understandable unsupported-file error and host callback state")

    driver.get(f"{APP}/?evidence=responsive-{COMMIT[:7]}")
    driver.set_window_rect(width=820, height=900)
    open_pdf(driver, wait, FIXTURES / "normal.pdf", 2)
    toggle = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Toggle thumbnails"]')
    toggle.send_keys(Keys.TAB)
    shot(driver, "09-firefox-tablet-focus.png", records, "Tablet-width alignment, scrollable toolbar, and visible keyboard focus")
finally:
    browser = {
        "name": driver.capabilities.get("browserName"),
        "version": driver.capabilities.get("browserVersion"),
        "platform": driver.capabilities.get("platformName"),
    }
    driver.quit()

manifest = {
    "capturedAtUtc": datetime.now(timezone.utc).isoformat(),
    "validatedCommit": COMMIT,
    "browser": browser,
    "desktopViewport": "1440x900",
    "tabletViewport": "820x900",
    "screenshots": records,
}
(OUTPUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
print(json.dumps(manifest, indent=2))
