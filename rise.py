import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import shutil
import time
import datetime

# Load konfigurasi dari .env
load_dotenv()

WALLET_ADDRESS = os.getenv('WALLET_ADDRESS')
TOKENS = os.getenv('TOKENS').split(',')  # Mengambil daftar token dari .env
MAX_DRIP_PER_TOKEN = int(os.getenv('MAX_DRIP_PER_TOKEN'))
CLAIM_INTERVAL = int(os.getenv('CLAIM_INTERVAL'))

CHROMEDRIVER_PATH = shutil.which("chromedriver")  # Ambil path chromedriver otomatis

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.binary_location = "/usr/bin/chromium-browser"  # Chromium di VPS

driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=options)

# Fungsi klaim token
def claim_token(token):
    print(f"[{datetime.datetime.now()}] 🚀 Klaim token {token}...")

    try:
        driver.get('https://faucet.testnet.riselabs.xyz/')
        time.sleep(2)

        # Pilih token
        select = Select(driver.find_element(By.ID, 'token'))
        select.select_by_visible_text(token)

        # Isi wallet
        wallet_input = driver.find_element(By.ID, 'wallet_address')
        wallet_input.send_keys(WALLET_ADDRESS)

        # Klik tombol klaim
        claim_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Request Tokens')]")
        claim_button.click()
        time.sleep(5)

        # Cek notifikasi
        alert = driver.find_element(By.CLASS_NAME, 'MuiAlert-message')
        result_text = alert.text
        print(f"[{datetime.datetime.now()}] 🔔 Hasil klaim: {result_text}")

        if "limit reached" in result_text.lower():
            print(f"[{datetime.datetime.now()}] ⛔ Token {token} limit hari ini.")
            return False  # token limit
        else:
            return True  # sukses klaim

    except Exception as e:
        print(f"[{datetime.datetime.now()}] ⚠️ Error saat klaim {token}: {e}")
        return True  # tetap coba token lain

# Loop klaim otomatis
def main():
    drip_log = {token: 0 for token in TOKENS}
    
    while True:
        if all(drip_log[token] >= MAX_DRIP_PER_TOKEN for token in TOKENS):
            print(f"[{datetime.datetime.now()}] ✅ Semua token limit hari ini. Tunggu 24 jam...\n")
            time.sleep(86400)  # Tunggu 1 hari (24 jam)
            drip_log = {token: 0 for token in TOKENS}  # Reset log harian
            continue
        
        for token in TOKENS:
            if drip_log[token] < MAX_DRIP_PER_TOKEN:
                if claim_token(token):
                    drip_log[token] += 1
                print(f"⏳ Menunggu {CLAIM_INTERVAL // 60} menit...\n")
                time.sleep(CLAIM_INTERVAL)

if __name__ == "__main__":
    main()

