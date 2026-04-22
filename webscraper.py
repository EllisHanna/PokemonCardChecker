import asyncio
import re
from playwright.async_api import async_playwright

CACHE = {}

async def change_currency(page, start, end):
    try:
        await page.get_by_text(start).first.click(timeout=3000)
        await page.get_by_text(end).first.click(timeout=3000)
    except:
        pass

async def search_card(page, name, number):
    search = page.locator("input[type='search']").first
    await search.wait_for(timeout=15000)

    await search.fill(f"{name} {number}")
    await search.press("Enter")

    await page.wait_for_timeout(3000)

    card = page.locator("span.font-bold", has_text=name).first
    try:
        await card.scroll_into_view_if_needed()
        await card.click(timeout=5000)
    except:
        pass

    await page.wait_for_timeout(3000)

async def extract_grade(page, grade_name):
    try:
        btn = page.locator("button", has_text=grade_name).first
        text = await btn.text_content()

        if not text:
            return None

        match = re.search(r"£[\d,]+(?:\.\d+)?", text)
        return match.group(0) if match else None
    except:
        return None

async def get_ungraded(page):
    try:
        el = page.locator("text=Ungraded").first
        container = el.locator("xpath=ancestor::div[1]")
        text = await container.text_content()

        match = re.search(r"£[\d,]+(?:\.\d+)?", text or "")
        return match.group(0) if match else None
    except:
        return None

async def get_image(page):
    try:
        img = page.locator("img").first
        src = await img.get_attribute("src")
        if not src:
            return None

        resp = await page.context.request.get(src)
        return await resp.body()
    except:
        return None

async def webscrape(name: str, number: str):
    key = f"{name}_{number}"
    if key in CACHE:
        return CACHE[key]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://app.getcollectr.com/", wait_until="domcontentloaded")

        await change_currency(page, "USD", "GBP")
        await search_card(page, name, number)

        ungraded = await get_ungraded(page)

        psa10 = await extract_grade(page, "PSA 10")
        psa9 = await extract_grade(page, "PSA 9")
        psa8 = await extract_grade(page, "PSA 8")

        bgs10 = await extract_grade(page, "BGS 10")
        cgc10 = await extract_grade(page, "CGC 10")
        cgc_pristine = await extract_grade(page, "CGC Pristine")

        img = await get_image(page)

        await browser.close()

        result = {
            "ungraded": ungraded,
            "psa10": psa10,
            "psa9": psa9,
            "psa8": psa8,
            "bgs10": bgs10,
            "cgc10": cgc10,
            "cgc_pristine": cgc_pristine,
            "image": img
        }

        CACHE[key] = result
        return result