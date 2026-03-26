import asyncio
import random
from fastapi import FastAPI
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

app = FastAPI()

@app.get("/scrape")
async def scrape(url: str = None):
    async with async_playwright() as p:
        try:
            # Randomize User Agent to look like a real iPhone/Mac
            user_agents = [
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            ]
            
            browser = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-blink-features=AutomationControlled"])
            context = await browser.new_context(user_agent=random.choice(user_agents))
            page = await context.new_page()
            
            # This is the "Magic" that hides the fact you are using a script
            await stealth_async(page)
            
            # Simulate human mouse movement before loading
            await page.goto(url, wait_until="networkidle", timeout=90000)
            
            # Wait a random amount of time (3-7 seconds)
            await asyncio.sleep(random.uniform(3, 7))
            
            content = await page.content()
            await browser.close()
            return {"status": "success", "data": content}
        except Exception as e:
            return {"status": "failed", "error": str(e)}

@app.get("/")
def health(): return {"status": "Hoopstreet Stealth Online"}
