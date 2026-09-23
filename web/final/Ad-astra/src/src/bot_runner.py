import json
import os
import secrets
import time
from urllib.parse import urlparse

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def _chrome_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument("--headless=true")
    options.add_argument("--no-sandbox")

    chrome_bin = os.environ.get("CHROME_BIN", "/usr/local/bin/chromium")
    chromedriver_bin = os.environ.get("CHROMEDRIVER_BIN", "/usr/local/bin/chromedriver")

    if chrome_bin and os.path.exists(chrome_bin):
        options.binary_location = chrome_bin
    if chromedriver_bin and os.path.exists(chromedriver_bin):
        service = Service(executable_path=chromedriver_bin)
        return webdriver.Chrome(service=service, options=options)

    return webdriver.Chrome(options=options)


def _target_extra_headers(target_url: str) -> dict[str, str]:
    host = (urlparse(target_url).hostname or "").lower()
    headers: dict[str, str] = {}
    if "ngrok" in host:
        headers["ngrok-skip-browser-warning"] = secrets.token_hex(8)
    if "loca.lt" in host or "localtunnel" in host:
        headers["bypass-tunnel-reminder"] = secrets.token_hex(8)
    raw_extra = os.environ.get("BOT_EXTRA_HEADERS")
    if raw_extra:
        try:
            parsed = json.loads(raw_extra)
            if isinstance(parsed, dict):
                headers.update({str(k): str(v) for k, v in parsed.items()})
        except json.JSONDecodeError:
            pass

    return headers


def run_admin_bot(target_url: str) -> None:
    base = "http://127.0.0.1:5024"
    admin_pw = os.environ.get("ADMIN_PASSWORD")
    if not admin_pw:
        raise RuntimeError("ADMIN_PASSWORD missing")

    driver = _chrome_driver()
    try:
        driver.set_page_load_timeout(10)
        driver.set_script_timeout(10)
        driver.execute_cdp_cmd("Network.enable", {})
        driver.get(f"{base}/motd")
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//h1[normalize-space()=\"Maestro's Word\"]"))
        )
        driver.get(f"{base}/login")
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, "username")))
        driver.find_element(By.NAME, "username").send_keys("admin")
        driver.find_element(By.NAME, "password").send_keys(admin_pw)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "inbox-page")))
        driver.get(f"{base}/flag")
        WebDriverWait(driver, 5).until(EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "OK"))
        extra_headers = _target_extra_headers(target_url)
        if extra_headers:
            def _apply_headers_to_open_windows(headers: dict[str, str]) -> None:
                handles = list(driver.window_handles)
                current = driver.current_window_handle if handles else None
                for handle in handles:
                    try:
                        driver.switch_to.window(handle)
                        driver.execute_cdp_cmd("Network.enable", {})
                        driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": headers})
                    except Exception:
                        continue
                if current and current in driver.window_handles:
                    driver.switch_to.window(current)

            _apply_headers_to_open_windows(extra_headers)
        driver.get(target_url)
        if extra_headers:
            deadline = time.time() + 10
            while time.time() < deadline:
                _apply_headers_to_open_windows(extra_headers)
                time.sleep(0.25)
            _apply_headers_to_open_windows({})
        else:
            time.sleep(10)
    finally:
        driver.quit()
