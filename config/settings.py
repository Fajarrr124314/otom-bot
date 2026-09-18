import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PROFILE_DIR = DATA_DIR / "browser_profile"

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)
PROFILE_DIR.mkdir(parents=True, exist_ok=True)

# Target Product Configuration
PRODUCT_URL = "https://shopee.co.id"  # Ganti dengan link produk incaran Anda

# Target Schedule: Waktu mulai Flash Sale dalam format "HH:MM:SS" (cth: "12:00:00")
# Kosongkan ("") jika ingin langsung mengeksekusi tanpa menunggu jam tertentu
TARGET_TIME = ""

# Pilihan Varian: teks varian (cth: "Merah", "XL", "256GB")
# Kosongkan ("") jika produk tidak memiliki varian atau varian bebas
TARGET_VARIANT = ""

# Browser Configuration
HEADLESS = False  # Wajib False agar Anda dapat memantau dan menyelesaikan CAPTCHA jika muncul
WINDOW_SIZE = "--start-maximized"

# Automation Performance (Ultra-Fast Tuning)
REFRESH_BEFORE_START = True   # Refresh halaman tepat saat TARGET_TIME tercapai
POLL_INTERVAL_SECONDS = 0.01  # Ultra-fast polling: cek setiap 10 milidetik (0.01 detik)
SEARCH_TIMEOUT_SECONDS = 25   # Batas waktu pencarian tombol setelah waktu target tiba
USE_IN_PAGE_INJECTION = True  # Injeksi script V8 langsung di browser untuk 0ms latency klik
