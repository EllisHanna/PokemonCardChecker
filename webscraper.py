import asyncio
from playwright.async_api import async_playwright

async def change_currency(page, start, end):
    dropdown = page.get_by_text(start).first
    await dropdown.wait_for(state="visible", timeout=15000)
    await dropdown.click()
    currency = page.get_by_text(end).first
    await currency.wait_for(state="visible", timeout=15000)
    await currency.click()

async def search_card(page, name, number):
    search_bar = page.locator("input").first
    await search_bar.wait_for(state="visible", timeout=15000)
    await search_bar.fill(f"{name} {number}")
    await page.wait_for_timeout(500)
    search_button = page.get_by_role("button", name="Search").first
    await search_button.wait_for(state="visible", timeout=15000)
    await search_button.click()
    title = page.locator("span.font-bold", has_text=name).first
    await title.wait_for(state="visible", timeout=15000)
    card_container = title.locator(
        "xpath=ancestor::div[contains(@class,'bg-card') and contains(@class,'cursor-pointer')]"
    ).first
    await card_container.scroll_into_view_if_needed()
    await card_container.click(force=True)

async def get_ungraded(page):
    ungraded_price = page.locator("span").filter(has_text="£").first
    await ungraded_price.wait_for(state="visible", timeout=10000)
    text = await ungraded_price.text_content()
    return text.strip() if text else None

async def get_grade_10(page):
    psa_label = page.locator("span", has_text="PSA 10").first
    await psa_label.wait_for(state="visible", timeout=10000)
    price_span = psa_label.locator("xpath=following-sibling::span[1]").first
    await price_span.wait_for(state="visible", timeout=10000)
    text = await price_span.text_content()
    return text.strip("() \n") if text else None

async def get_image(page):
    img = page.locator("img[src*='product_']").first
    await img.wait_for(state="visible", timeout=10000)
    img_url = await img.get_attribute("src")
    if not img_url:
        raise Exception("Image URL not found")
    response = await page.request.get(img_url)
    return await response.body()

async def webscrape(name: str, number: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("https://app.getcollectr.com/")
        await page.wait_for_timeout(2000)
        await change_currency(page, "USD", "GBP")
        await search_card(page, name, number)
        ungraded_price = await get_ungraded(page)
        graded_price = await get_grade_10(page)
        img_bytes = await get_image(page)
        await browser.close()
        return ungraded_price, graded_price, img_bytes
