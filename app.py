import asyncio
import random
import os
from fastapi import FastAPI
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

app = FastAPI()

# List of real device User-Agents to rotate
USER_AGENTS = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
]

@app.get("/scrape")
async def scrape(url: str = None):
    if not url:
        return {"status": "error", "message": "No URL provided"}

    async with async_playwright() as p:
        try:
            # Launch browser with "No-Sandbox" for Northflank/Docker
            browser = await p.chromium.launch(
                headless=True, 
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-blink-features=AutomationControlled"]
            )

            # Pick a random User-Agent for this specific request
            chosen_agent = random.choice(USER_AGENTS)

            # Create context with the random agent
            # If you have a 'cookies.json' file, we can load it here to use a dummy account
            context_args = {"user_agent": chosen_agent}
            
            # Check if you uploaded a dummy account state to your repo
            if os.path.exists("state.json"):
                context = await browser.new_context(storage_state="state.json", **context_args)
            else:
                context = await browser.new_context(**context_args)

            page = await context.new_page()
            
            # Apply stealth to hide Playwright fingerprints
            await stealth_async(page)
            
            # Navigate to TikTok with a longer timeout for cloud servers
            await page.goto(url, wait_until="networkidle", timeout=90000)
            
            # Human-like delay to let the "Puzzle Piece" pass or content load
            await asyncio.sleep(random.uniform(5, 8))
            
            content = await page.content()
            await browser.close()
            
            return {
                "status": "success", 
                "device_emulated": chosen_agent,
                "data": content
            }
        except Exception as e:
            return {"status": "failed", "error": str(e)}

@app.get("/")
def health():
    return {"status": "Hoopstreet Stealth Scraper is Online"}
