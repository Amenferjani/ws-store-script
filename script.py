import imaplib
import os
import email
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

# ==============================
# EMAIL CONFIG
# ==============================
EMAIL = os.environ["EMAIL"]
PASSWORD = os.environ["PASSWORD"]
IMAP_SERVER = os.environ["IMAP_SERVER"]

# ==============================
# SELENIUM CONFIG
# ==============================
WEB_BUTTON_TEXT = "Confirm Update"
BUTTON_TEXT = "Yes, This Was Me"

def get_latest_netflix_link():
    """Connects to inbox and extracts the latest Netflix confirmation link from UNSEEN emails."""
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL, PASSWORD)
    mail.select("inbox")

    # Search for unseen emails from the sender
    status, messages = mail.search(None, '(UNSEEN FROM "info@account.netflix.com")')
    email_ids = messages[0].split()

    if not email_ids:
        print("❌ No new emails found.")
        return None

    latest_id = email_ids[-1]  # get the latest email
    status, msg_data = mail.fetch(latest_id, "(RFC822)")
    raw_msg = msg_data[0][1]
    msg = email.message_from_bytes(raw_msg)

    # Mark the email as seen
    mail.store(latest_id, '+FLAGS', '\\Seen')

    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                body = part.get_payload(decode=True).decode()
                break
    else:
        body = msg.get_payload(decode=True).decode()

    # Parse HTML and extract links
    soup = BeautifulSoup(body, "html.parser")
    for a in soup.find_all("a", href=True):
        if BUTTON_TEXT in a.text:
            return a["href"]

    return None

def get_netflix_page_info(url):
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless=new")  # headless for EC2
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--user-data-dir=/tmp/selenium_profile")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(url)
        print(f"Navigated to {url}")

        wait = WebDriverWait(driver, 10)  # short wait for expired links
        try:
            button_element = wait.until(EC.visibility_of_element_located(
                (By.XPATH, f"//a[contains(text(), '{WEB_BUTTON_TEXT}')] | //button[contains(text(), '{WEB_BUTTON_TEXT}')]")
            ))
        except:
            print("⚠️ Link expired or button not found, skipping...")
            return None

        # CLICK the button
        button_element.click()
        print(f"✅ Clicked the button: '{button_element.text}'")

        # Wait a bit so JavaScript updates the log area
        time.sleep(2)

        # Grab the log area text (from <div id="logArea">)
        log_area = driver.find_element(By.ID, "logArea")
        log_text = log_area.text

        print("📜 Log after click:")
        print(log_text)

        return driver.page_source

    finally:
        driver.quit()


if __name__ == "__main__":
    print("Starting the script...")
    link = get_latest_netflix_link()

    if link:
        page_html = get_netflix_page_info(link)
        if page_html:
            print("\n--- HTML Page Processed Successfully ---")
        else:
            print("⚠️ Link was expired or invalid.")
    else:
        print("No new valid email links found.")
