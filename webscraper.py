import asyncio
import time
from playwright.async_api import async_playwright

async def change_currency(page, start, end):
    dropdown = page.get_by_text(start).first
    await dropdown.click()
    currency = page.get_by_text(end).first
    await currency.click()

async def search_card(page, name, number):
    search_bar = page.locator("input").first
    await search_bar.fill(f"{name} {number}")
    search_button = page.get_by_role("button", name="Search")
    await search_button.click()
    result = page.locator("h3").filter(has_text=f"{name[0].upper()}{name[1:]}").first
    await result.click()

async def get_ungraded(page):
    ungraded_price = page.locator("span").filter(has_text="£").first
    print(await ungraded_price.text_content())
    return await ungraded_price.text_content()

async def get_grade_10(page):
    graded_container = page.locator("#legend-container")
    psa_label = graded_container.locator("text=PSA 10")
    if not await psa_label.count():
        return " "
    graded_price = psa_label.locator("xpath=./following-sibling::*[1] | ../*[contains(., '£')]")
    try:
        graded_price_text = await graded_price.text_content()
        if graded_price_text:
            graded_price_text = graded_price_text.strip("() \n")
        else:
            graded_price_text = " "
    except Exception:
        graded_price_text = " "
    print(graded_price_text)
    return graded_price_text

async def get_image(page):
    img = page.locator("main img").first
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