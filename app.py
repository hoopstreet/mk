import asyncio
from fastapi import FastAPI
from playwright.async_api import async_playwright

app = FastAPI()

@app.get("/scrape")
async def scrape(url: str = None):
    if not url:
        return {"status": "error", "message": "No URL provided"}

    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
            context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            page = await context.new_page()
            
            # Navigate to TikTok Product URL
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(5) # Wait for details to load
            
            content = await page.content()
            await browser.close()
            return {"status": "success", "data": content}
        except Exception as e:
            return {"status": "failed", "error": str(e)}

@app.get("/")
def health_check():
    return {"status": "Hoopstreet Scraper is Online"}
