import os, pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Selenium runs in a separate container; host.docker.internal reaches the published app port.
APP_URL=os.getenv("UI_APP_URL","http://host.docker.internal:5000")
SELENIUM_URL=os.getenv("SELENIUM_URL","http://localhost:4444/wd/hub")

@pytest.fixture
def driver():
    options=webdriver.ChromeOptions()
    options.add_argument("--headless=new"); options.add_argument("--no-sandbox"); options.add_argument("--disable-dev-shm-usage")
    d=webdriver.Remote(command_executor=SELENIUM_URL, options=options)
    d.set_window_size(1280,900)
    yield d
    d.quit()

def test_login_search_book_cancel(driver):
    driver.get(APP_URL)
    wait=WebDriverWait(driver,10)
    wait.until(EC.presence_of_element_located((By.ID,"username")))
    assert "Travel Booking Demo" in driver.title
    driver.find_element(By.ID,"username").send_keys("demo")
    driver.find_element(By.ID,"password").send_keys("demo123")
    driver.find_element(By.ID,"loginBtn").click()
    wait.until(EC.text_to_be_present_in_element((By.ID,"message"),"Login successful"))
    driver.find_element(By.ID,"searchBtn").click()
    wait.until(EC.presence_of_element_located((By.ID,"trip-TR101")))
    driver.find_element(By.ID,"trip-TR102").click()
    driver.find_element(By.ID,"bookBtn").click()
    wait.until(EC.text_to_be_present_in_element((By.ID,"bookingStatus"),"TR102"))
    driver.find_element(By.ID,"cancelBtn").click()
    wait.until(EC.text_to_be_present_in_element((By.ID,"bookingStatus"),"Booking cancelled"))
