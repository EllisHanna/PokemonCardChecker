import asyncio
from playwright.async_api import async_playwright

CACHE = {}

async def change_currency(page, start, end):
    await page.get_by_text(start).first.click()
    await page.get_by_text(end).first.click()

async def search_card(page, name, number):
    search_bar = page.locator("input").first
    await search_bar.fill(f"{name} {number}")
    await page.get_by_role("button", name="Search").first.click()

    card = page.locator(
        "span.font-bold",
        has_text=name
    ).first.locator(
        "xpath=ancestor::div[contains(@class,'bg-card') and contains(@class,'cursor-pointer')]"
    )

    await card.scroll_into_view_if_needed()
    await card.click(force=True)

async def get_ungraded(page):
    ungraded_price = page.locator("span").filter(has_text="£").first
    text = await ungraded_price.text_content()
    return text.strip() if text else None

async def get_grade_10(page):
    psa_label = page.locator("span", has_text="PSA 10").first
    price_span = psa_label.locator("xpath=following-sibling::span[1]").first
    text = await price_span.text_content()
    return text.strip("() \n") if text else None

async def get_image(page):
    img = page.locator("img[src*='product_']").first
    img_url = await img.get_attribute("src")
    response = await page.context.request.get(img_url)
    return await response.body()

async def webscrape(name: str, number: str):
    key = f"{name}_{number}"
    if key in CACHE:
        return CACHE[key]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto(
            "https://app.getcollectr.com/",
            wait_until="domcontentloaded"
        )

        await change_currency(page, "USD", "GBP")
        await search_card(page, name, number)

        ungraded_price = await get_ungraded(page)
        graded_price = await get_grade_10(page)
        img_bytes = await get_image(page)

        await browser.close()

        result = (ungraded_price, graded_price, img_bytes)
        CACHE[key] = result
        return result