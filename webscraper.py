import asyncio
from playwright.async_api import async_playwright

async def change_currency(page, start, end):
    dropdown = page.get_by_text(start).first
    await dropdown.click()
    currency = page.get_by_text(end).first
    await currency.click()

async def search_card(page, name, number):
    search_bar = page.locator("input").first
    await search_bar.fill(f"{name} {number}")
    await page.wait_for_timeout(800)
    search_button = page.get_by_role("button", name="Search")
    await search_button.click()
    title = page.locator("span.font-bold", has_text=name).first
    await title.wait_for(state="visible", timeout=10000)
    card = title.locator("xpath=ancestor::div[contains(@class,'bg-card') and contains(@class,'cursor-pointer')]")
    await card.first.scroll_into_view_if_needed()
    await card.first.click(force=True)

async def get_ungraded(page):
    ungraded_price = page.locator("span").filter(has_text="£").first
    text = await ungraded_price.text_content()
    print(text)
    return text

async def get_grade_10(page):
    psa_label = page.locator("span", has_text="PSA 10").first
    await psa_label.wait_for(state="visible", timeout=10000)
    price_span = psa_label.locator("xpath=following-sibling::span[1]")
    text = await price_span.text_content()
    text = text.strip("() \n") if text else " "
    print(text)
    return text

async def get_image(page):
    img = page.locator("img[src*='product_']").first
    img_url = await img.get_attribute("src")
    response = await page.request.get(img_url)
    return await response.body()

async def webscrape(name, number):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://app.getcollectr.com/")
        await change_currency(page, "USD", "GBP")
        await search_card(page, name, number)
        ungraded_price = await get_ungraded(page)
        graded_price = await get_grade_10(page)
        img_byte = await get_image(page)
        await browser.close()
        return ungraded_price, graded_price, img_byte
