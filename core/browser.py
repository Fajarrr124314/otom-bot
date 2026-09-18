import sys
from pathlib import Path
from playwright.async_api import async_playwright, BrowserContext
from config import settings

async def create_browser_context(playwright_instance) -> BrowserContext:
    """
    Membuat persistent context browser dengan Chromium.
    Menyimpan cookies, local storage, dan session login di settings.PROFILE_DIR.
    """
    args = [
        settings.WINDOW_SIZE,
        "--disable-blink-features=AutomationControlled",
        "--no-sandbox",
        "--disable-infobars",
        "--disable-background-timer-throttling",
        "--disable-backgrounding-occluded-windows",
        "--disable-renderer-backgrounding",
        "--disable-ipc-flooding-protection",
        "--enable-features=NetworkService,NetworkServiceInProcess",
    ]
    
    context = await playwright_instance.chromium.launch_persistent_context(
        user_data_dir=str(settings.PROFILE_DIR),
        headless=settings.HEADLESS,
        viewport=None,
        args=args,
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    )
    return context
