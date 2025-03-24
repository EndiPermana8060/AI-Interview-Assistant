import pytesseract
import cv2
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from PIL import Image
import numpy as np

class GoogleMeetBot:
    def __init__(self, meet_url):
        self.meet_url = meet_url
        self.screenshot_path = "meet_screenshot.png"
        self.driver = self._setup_driver()
    
    def _setup_driver(self):
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--remote-debugging-port=9222")
        options.add_argument("user-data-dir=C:/Users/USER/AppData/Local/Google/Chrome/SeleniumProfile")
        options.add_argument("--profile-directory=Default")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--force-device-scale-factor=1")
        return webdriver.Chrome(service=Service(), options=options)
    
    def open_meet(self):
        self.driver.get(self.meet_url)
        time.sleep(5)
    
    def take_screenshot(self):
        self.driver.save_screenshot(self.screenshot_path)
        print(f"📸 Screenshot disimpan: {self.screenshot_path}")
    
    def perform_ocr(self):
        img = cv2.imread(self.screenshot_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray, lang="eng+ind")
        print("📝 Hasil OCR:", text)
        return text
    
    def click_join_button(self, text):
        button_texts = ["Ask to join", "Join now", "Minta bergabung", "Gabung sekarang"]
        
        if any(btn_text in text for btn_text in button_texts):
            print("✅ Tombol ditemukan dalam OCR!")
            self.driver.execute_script("document.elementFromPoint(800, 500).click();")
        else:
            print("⚠ Tombol tidak ditemukan dalam OCR! Mencoba metode Selenium...")
            self._click_button_selenium()
    
    def _click_button_selenium(self):
        try:
            join_button = self.driver.find_element(
                "xpath",
                "//span[contains(text(),'Ask to join') or contains(text(),'Join Now') or contains(text(),'Minta bergabung') or contains(text(),'Gabung Sekarang')]"
            )
            join_button.click()
            print("✅ Tombol berhasil diklik dengan XPath!")
        except:
            print("⚠ Tombol tidak ditemukan dengan XPath. Mencoba CSS Selector...")
            try:
                join_button = self.driver.find_element("css selector", "button[jsname='Qx7uuf']")
                join_button.click()
                print("✅ Tombol berhasil diklik dengan CSS Selector!")
            except:
                print("⚠ Tombol tetap tidak ditemukan!")
    
    def run(self):
        try:
            print("✅ ChromeDriver berjalan dalam mode headless!")
            self.open_meet()
            self.take_screenshot()
            text = self.perform_ocr()
            self.click_join_button(text)
            
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            print("❌ Program dihentikan oleh pengguna.")
        except Exception as e:
            print("❌ Error:", e)
        finally:
            self.driver.quit()