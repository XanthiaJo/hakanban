"""Run the Hakanban browser test HTML pages in a headless Chromium."""

import os
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urljoin

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait
except ImportError as err:
    print("selenium is not installed: pip install selenium")
    raise SystemExit(1) from err


def find_chromedriver():
    """Locate chromedriver on the PATH or in common places."""
    for name in ("chromedriver", "chromedriver.exe"):
        for path in os.environ["PATH"].split(os.pathsep):
            candidate = Path(path) / name
            if candidate.exists():
                return str(candidate)
    # Common CI locations
    candidates = [
        "/usr/bin/chromedriver",
        "/usr/local/bin/chromedriver",
        "/usr/lib/chromium-browser/chromedriver",
    ]
    for c in candidates:
        if Path(c).exists():
            return c
    return None


def find_chrome():
    """Locate the Chrome/Chromium binary."""
    for name in ("chromium", "chromium-browser", "chrome", "google-chrome", "google-chrome-stable"):
        for path in os.environ["PATH"].split(os.pathsep):
            candidate = Path(path) / name
            if candidate.exists():
                return str(candidate)
    # Common CI locations
    candidates = [
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
    ]
    for c in candidates:
        if Path(c).exists():
            return c
    return None


def start_server():
    """Start an HTTP server for the repo root."""
    repo = Path(__file__).resolve().parent.parent.parent
    proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", "0"],
        cwd=repo,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    # Read the port from stdout
    line = ""
    for _ in range(50):
        line = proc.stdout.readline()
        if line:
            break
        time.sleep(0.1)
    # Output is "Serving HTTP on ... port 12345 ..."
    port = int(line.split("port")[-1].split(" ")[0])
    return proc, f"http://127.0.0.1:{port}"


def run_test(driver, base_url, path):
    """Open a browser test page and return the summary text."""
    url = urljoin(base_url, path)
    driver.get(url)
    wait = WebDriverWait(driver, 30)
    # Wait for the summary line to be added at the end
    wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(),'passed')]")))
    # Look for any fail lines
    fails = driver.find_elements(By.CSS_SELECTOR, ".fail")
    return len(fails) == 0, driver.find_element(By.TAG_NAME, "body").text


def main():
    driver_path = find_chromedriver()
    chrome_path = find_chrome()

    if not driver_path:
        print("chromedriver not found; install chromium-chromedriver and try again")
        return 1
    if not chrome_path:
        print("chromium/chrome binary not found; install chromium and try again")
        return 1

    server, base_url = start_server()
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.binary_location = chrome_path

        service = Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        try:
            all_pass = True
            tests = [
                ("tests/browser/test-display-opts.html", "Display options"),
                ("tests/browser/test-card-detail.html", "Card detail"),
            ]
            for path, name in tests:
                ok, body = run_test(driver, base_url, path)
                all_pass = all_pass and ok
                print(f"--- {name} ({path}) ---")
                print(body)
                print()
            return 0 if all_pass else 1
        finally:
            driver.quit()
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()


if __name__ == "__main__":
    sys.exit(main())
