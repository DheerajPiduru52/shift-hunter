from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import requests
from datetime import datetime

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = ""
TELEGRAM_CHAT_ID = ""

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, json=payload)
        print("Telegram notification sent.")
    except Exception as e:
        print("Failed to send Telegram notification:", e)

# Setup Selenium WebDriver
def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# Login Function to Handle University Login and MFA
def login(driver, url):
    driver.get(url)
    time.sleep(3)  # Wait for the page to load
    
    # Click on 'University Account' button
    try:
        university_account_button = driver.find_element(By.XPATH, "//button[contains(text(), 'University Account')]")
        university_account_button.click()
        time.sleep(3)
    except Exception as e:
        print("University Account button not found or already redirected.", e)
    
    # Wait for manual login and MFA
    input("Please complete the login and MFA process, then press Enter to continue...")

# Convert time string to 24-hour format
def parse_time(time_str):
    return datetime.strptime(time_str, "%I:%M %p").time()

# Check if shift time falls within restricted hours
def is_restricted_time(shift_time):
    try:
        start_time_str, end_time_str = shift_time.split(" - ")
        start_time = parse_time(start_time_str)
        end_time = parse_time(end_time_str)
        
        restricted_periods = [
            (parse_time("6:45 AM"), parse_time("10:00 AM")),
            (parse_time("10:00 PM"), parse_time("1:00 AM"))
        ]
        
        for r_start, r_end in restricted_periods:
            if start_time < r_end and end_time > r_start:
                return True
    except Exception as e:
        print("Error parsing time:", e)
    return False

# Fetch and Auto-Pick Available Shifts
def fetch_and_pick_shifts(driver):
    driver.get("https://utdallas.dserec.com/staff/employees/tradecenter")
    time.sleep(3)  # Give time for page to load
    
    try:
        WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located((By.XPATH, "//tr[starts-with(@id, 'shift')]")))
        shift_rows = driver.find_elements(By.XPATH, "//tr[starts-with(@id, 'shift')]")
        print(f"Found {len(shift_rows)} shift rows on the page.")
        
        for row in shift_rows:
            columns = row.find_elements(By.TAG_NAME, "td")
            
            if len(columns) < 4:
                print("Skipping row due to missing columns:", [col.text for col in columns])
                continue
            
            date = columns[0].text.strip()
            time_slot = columns[1].text.strip()
            job = columns[2].text.strip()
            location = columns[3].text.strip()
            
            # Extract shift comment if available
            try:
                comment_element = columns[2].find_element(By.CLASS_NAME, "notes")
                comment = comment_element.get_attribute("data-original-title").strip()
            except Exception:
                comment = "No special comment"
            
            # Apply exclusion filters
            if "leadership" in comment.lower() or "shift lead" in comment.lower():
                print(f"Skipping shift due to leadership restriction: {time_slot}")
                continue
            
            if is_restricted_time(time_slot):
                print(f"Skipping shift due to time restriction: {time_slot}")
                continue
            
            # Find and click the request button
            try:
                request_button = columns[6].find_element(By.TAG_NAME, "button")
                request_button.click()
                time.sleep(2)
                print(f"Shift {time_slot} requested successfully!")
                send_telegram_message(f"✅ Shift Picked: {date} | {time_slot} | {job} | {location}")
                
                # Handle confirmation popup
                try:
                    confirm_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'ACCEPT')]")))
                    confirm_button.click()
                    print("Shift successfully accepted!")
                except Exception as e:
                    print("No confirmation popup found or unable to accept shift.", e)
            except Exception:
                print(f"No request button found for shift {time_slot}.")
                continue
        
    except Exception as e:
        print("❌ Error fetching shift table:", e)

# Main Execution
driver = setup_driver()
login(driver, "https://utdallas.dserec.com/staff/auth?redirect=https%3A%2F%2Futdallas.dserec.com%2Fstaff%2Femployees%2Fdetails")

while True:
    fetch_and_pick_shifts(driver)
    time.sleep(2)  # Refresh every 2 seconds to check for new shifts

driver.quit()
