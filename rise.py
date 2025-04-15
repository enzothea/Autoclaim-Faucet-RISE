from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
import time
import datetime

# CONFIG
WALLET_ADDRESS = '0xYourWalletAddressHere'
CHROMEDRIVER_PATH = 'C:/path/to/chromedriver.exe'
URL = 'https://faucet.testnet.riselabs.xyz/'
TOKENS = ['ETH', 'USDC', 'WETH', 'DAI']  # Kamu bisa tambah token di sini
MAX_DRIP_PER_TOKEN = 3
CLAIM_INTERVAL = 3600  # 60 menit

# Log drip per token (reset tiap hari)
drip_log = {token: 0 for token in TOKENS}

def claim_token(token):
    print(f"[{datetime.datetime.now()}] 🚀 Klaim token {token} ke-{drip_log[token]+1}...")

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=options)

    try:
        driver.get(URL)
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
            drip_log[token] += 1
            return True  # sukses klaim

    except Exception as e:
        print(f"[{datetime.datetime.now()}] ⚠️ Error saat klaim {token}: {e}")
        return True  # anggap tetap coba token lain

    finally:
        driver.quit()

def all_token_limits_reached():
    return all(drip_log[token] >= MAX_DRIP_PER_TOKEN for token in TOKENS)

# 🌀 Looping otomatis harian
while True:
    if all_token_limits_reached():
        print(f"[{datetime.datetime.now()}] ✅ Semua token limit hari ini. Tunggu 24 jam...\n")
        time.sleep(86400)  # Tunggu 1 hari (24 jam)
        drip_log = {token: 0 for token in TOKENS}  # Reset log harian
        continue

    for token in TOKENS:
        if drip_log[token] < MAX_DRIP_PER_TOKEN:
            claim_token(token)
            print(f"⏳ Menunggu {CLAIM_INTERVAL // 60} menit...\n")
            time.sleep(CLAIM_INTERVAL)
