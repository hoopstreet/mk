import asyncio
from fastapi import FastAPI
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

app = FastAPI()

@app.get("/scrape")
async def scrape(url: str = None):
    if not url:
        return {"status": "error", "message": "No URL provided"}

    async with async_playwright() as p:
        try:
            # Optimized for low RAM (256MB)
            browser = await p.chromium.launch(
                headless=True, 
                args=[
                    "--no-sandbox", 
                    "--disable-setuid-sandbox", 
                    "--disable-dev-shm-usage", 
                    "--disable-accelerated-2d-canvas", 
                    "--no-first-run", 
                    "--no-zygote", 
                    "--single-process"
                ]
            )
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            
            # Apply stealth to bypass simple bot detection
            await stealth_async(page)
            
            # Go to TikTok URL
            await page.goto(url, wait_until="networkidle", timeout=60000)
            
            # Wait for content to render
            await asyncio.sleep(5)
            
            content = await page.content()
            await browser.close()
            
            return {"status": "success", "data": content}
        except Exception as e:
            return {"status": "failed", "error": str(e)}

@app.get("/")
def health():
    return {"status": "Hoopstreet Scraper is Online"}
