import asyncio
import time
from playwright.async_api import BrowserContext, Page
from config import settings
from core.scheduler import wait_until_target

async def setup_login_session(page: Page):
    """
    Fungsi untuk inisialisasi awal profil:
    Membuka halaman Shopee agar pengguna dapat login secara manual.
    Sesi login akan tersimpan permanen di folder data/browser_profile.
    """
    print("\n" + "="*60)
    print("[SETUP] Membuka Shopee untuk login awal...")
    print("Silakan login akun Anda di jendela browser yang terbuka.")
    print("Setelah berhasil login dan masuk ke beranda, tutup jendela browser atau tekan ENTER di terminal.")
    print("="*60 + "\n")
    
    await page.goto("https://shopee.co.id/buyer/login", wait_until="domcontentloaded")
    
    # Tunggu pengguna melakukan login
    while True:
        try:
            # Periksa apakah sudah berhasil masuk (ada elemen akun / logout / username)
            is_logged_in = await page.locator(".shopee-avatar, .navbar__username").count() > 0
            if is_logged_in:
                print("\n[+] Terdeteksi sesi akun telah login!")
                break
        except Exception:
            pass
        await asyncio.sleep(2)
        
    print("[+] Sesi login berhasil disimpan ke data/browser_profile.")

async def inject_fast_clicker(page: Page, target_variant: str):
    """
    Menyuntikkan skrip mikro langsung ke engine V8 browser.
    Berjalan setiap 5 milidetik di dalam browser (0ms latency Python IPC).
    """
    js_code = f"""
    (() => {{
        window.__fast_flash_triggered = false;
        const targetVar = "{target_variant}";
        
        const microLoop = () => {{
            if (window.__fast_flash_triggered) return;
            
            // 1. Pilih varian jika ada
            if (targetVar) {{
                const varBtns = Array.from(document.querySelectorAll('button.product-variation'));
                for (const btn of varBtns) {{
                    if (btn.innerText.includes(targetVar) && !btn.classList.contains('product-variation--selected')) {{
                        btn.click();
                        break;
                    }}
                }}
            }}
            
            // 2. Cari tombol 'Beli Sekarang'
            const buttons = Array.from(document.querySelectorAll('button'));
            for (const btn of buttons) {{
                const text = (btn.innerText || "").toLowerCase();
                if (text.includes('beli sekarang')) {{
                    const isDisabled = btn.disabled || btn.getAttribute('aria-disabled') === 'true';
                    if (!isDisabled) {{
                        window.__fast_flash_triggered = true;
                        btn.click();
                        console.log("[IN-PAGE ULTRA FAST] Klik 'Beli Sekarang' berhasil dieksekusi!");
                        return true;
                    }}
                }}
            }}
            return false;
        }};

        const intervalId = setInterval(() => {{
            if (microLoop()) {{
                clearInterval(intervalId);
            }}
        }}, 5);
    }})();
    """
    try:
        await page.evaluate(js_code)
    except Exception:
        pass

async def execute_flash_sale(page: Page):
    """
    Alur eksekusi flash sale dengan kecepatan ultra-tinggi:
    1. Membuka URL produk target
    2. Menunggu waktu target (jika disetel di settings.py)
    3. Refresh tepat waktu
    4. Mengaktifkan injeksi V8 in-page (5ms loop) + Python loop paralel (10ms)
    5. Klik instan tanpa menunggu network idle (force=True, no_wait_after=True)
    6. Navigasi ke halaman checkout
    """
    if not settings.PRODUCT_URL or settings.PRODUCT_URL == "https://shopee.co.id":
        print("[-] Peringatan: PRODUCT_URL belum diatur di config/settings.py!")
        return

    print(f"\n[*] Menavigasi ke halaman produk:\n    {settings.PRODUCT_URL}")
    await page.goto(settings.PRODUCT_URL, wait_until="domcontentloaded")

    # 1. Menunggu hingga waktu target tiba
    if settings.TARGET_TIME:
        await wait_until_target(settings.TARGET_TIME)
        
        # Refresh halaman tepat pada detik target
        if settings.REFRESH_BEFORE_START:
            print("[*] [ULTRA-SPEED] Melakukan refresh cepat...")
            await page.reload(wait_until="domcontentloaded")

    print("[*] [ULTRA-SPEED] Mengaktifkan deteksi instan (In-Page JS + Python Poller)...")
    
    # 2. Injeksi in-page script langsung ke V8 browser untuk 0ms latency
    if getattr(settings, "USE_IN_PAGE_INJECTION", True):
        await inject_fast_clicker(page, settings.TARGET_VARIANT)

    start_time = time.time()
    clicked_buy = False

    # 3. Paralel Python Poller (Fallback & Akselerator)
    while time.time() - start_time < settings.SEARCH_TIMEOUT_SECONDS:
        try:
            # Periksa apakah in-page script sudah berhasil klik
            in_page_done = await page.evaluate("() => window.__fast_flash_triggered === true")
            if in_page_done:
                print("\n" + "="*50)
                print("[+] [ULTRA-SPEED] Tombol 'Beli Sekarang' berhasil diklik via IN-PAGE JS!")
                print("="*50 + "\n")
                clicked_buy = True
                break

            # A. Pilih Varian via Playwright jika belum terklik
            if settings.TARGET_VARIANT:
                var_btn = page.locator(f"button.product-variation:has-text('{settings.TARGET_VARIANT}')").first
                if await var_btn.count() > 0:
                    class_attr = await var_btn.get_attribute("class") or ""
                    if "product-variation--selected" not in class_attr:
                        await var_btn.click(timeout=100, force=True, no_wait_after=True)

            # B. Deteksi tombol 'Beli Sekarang' via Playwright
            buy_btn = page.locator("button:has-text('Beli Sekarang'), button:has-text('beli sekarang')").first
            if await buy_btn.count() > 0:
                is_disabled = await buy_btn.get_attribute("disabled") is not None or \
                              await buy_btn.get_attribute("aria-disabled") == "true"
                
                if not is_disabled:
                    # force=True & no_wait_after=True untuk trigger instan tanpa delay Playwright
                    await buy_btn.click(timeout=200, force=True, no_wait_after=True)
                    print("\n" + "="*50)
                    print("[+] [ULTRA-SPEED] Tombol 'Beli Sekarang' berhasil diklik via Python Core!")
                    print("="*50 + "\n")
                    clicked_buy = True
                    break
        except Exception:
            pass

        await asyncio.sleep(settings.POLL_INTERVAL_SECONDS)

    if not clicked_buy:
        print("[-] Waktu pencarian habis. Tombol beli belum aktif atau stok tidak tersedia.")
        return

    # 4. Menunggu navigasi ke halaman checkout
    print("[*] Menunggu transisi ke halaman checkout...")
    try:
        await page.wait_for_url("**/checkout**", timeout=8000)
        print("[+] Telah berada di halaman checkout!")
        print("[!] Silakan konfirmasi metode pembayaran, voucher, dan tekan 'Buat Pesanan' secara manual.")
    except Exception:
        print("[!] Tetap pantau jendela browser untuk konfirmasi akhir pembayaran.")
