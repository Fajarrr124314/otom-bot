import asyncio
import sys
from playwright.async_api import async_playwright
from config import settings
from core.browser import create_browser_context
from core.bot import setup_login_session, execute_flash_sale

def print_header():
    print("=" * 60)
    print("     SHOPEE FLASH SALE ASSISTANT (PYTHON + PLAYWRIGHT)     ")
    print("=" * 60)

def display_config():
    print("\n--- Konfigurasi Saat Ini (config/settings.py) ---")
    print(f" • URL Target     : {settings.PRODUCT_URL}")
    print(f" • Target Jadwal  : {settings.TARGET_TIME or 'Langsung / Manual'}")
    print(f" • Varian Produk  : {settings.TARGET_VARIANT or 'Tidak ada / Bebas'}")
    print(f" • Profil Browser : {settings.PROFILE_DIR}")
    print(f" • Refresh on Time: {settings.REFRESH_BEFORE_START}")
    print("-" * 50 + "\n")

async def run_setup():
    async with async_playwright() as p:
        context = await create_browser_context(p)
        page = context.pages[0] if context.pages else await context.new_page()
        await setup_login_session(page)
        print("[i] Menutup browser setup...")
        await context.close()

async def run_bot():
    display_config()
    confirm = input("Apakah Anda siap menjalankan asisten? (y/n): ").strip().lower()
    if confirm != 'y':
        print("[*] Dibatalkan.")
        return

    async with async_playwright() as p:
        context = await create_browser_context(p)
        page = context.pages[0] if context.pages else await context.new_page()
        
        try:
            await execute_flash_sale(page)
            # Berikan waktu agar pengguna dapat menyelesaikan checkout
            print("\n[i] Jendela browser akan tetap terbuka selama 2 menit untuk konfirmasi akhir Anda...")
            await asyncio.sleep(120)
        except KeyboardInterrupt:
            print("\n[!] Dihentikan oleh pengguna.")
        finally:
            await context.close()

def main():
    print_header()
    while True:
        print("Menu Utama:")
        print(" [1] Login Akun Shopee (Setup Profile Sesi)")
        print(" [2] Jalankan Asisten Flash Sale")
        print(" [3] Lihat Pengaturan (Settings)")
        print(" [4] Keluar")
        
        choice = input("\nPilih opsi [1-4]: ").strip()
        
        if choice == "1":
            asyncio.run(run_setup())
        elif choice == "2":
            asyncio.run(run_bot())
        elif choice == "3":
            display_config()
        elif choice == "4":
            print("\nSampai jumpa!")
            sys.exit(0)
        else:
            print("[-] Pilihan tidak valid, silakan coba lagi.\n")

if __name__ == "__main__":
    main()
