import asyncio
import aiohttp
import aiofiles
import os
import re

API_KEY = os.getenv("POKEMONTCG_API_KEY")
API_BASE = "https://api.pokemontcg.io/v2/cards"

OUTPUT_DIR = "card_images"
PAGE_SIZE = 250
PAGE_DELAY = 0.5
MAX_RETRIES = 5
MAX_CONCURRENT_DOWNLOADS = 4

SEM = asyncio.Semaphore(MAX_CONCURRENT_DOWNLOADS)

def sanitize(text):
    return re.sub(r'[<>:"/\\|?*]', '', text)

async def fetch_cards_page(session, q, page):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            params = {"q": q, "page": page, "pageSize": PAGE_SIZE}
            print(f"[REQUEST] q={q} page={page} attempt={attempt}")
            async with session.get(
                API_BASE,
                params=params,
                headers={"X-Api-Key": API_KEY},
                timeout=aiohttp.ClientTimeout(total=90)
            ) as resp:
                print(f"[STATUS] {resp.status}")
                resp.raise_for_status()
                return await resp.json()
        except Exception as e:
            print(f"[ERROR] {e}")
            if attempt == MAX_RETRIES:
                return None
            await asyncio.sleep(attempt * 2)
    return None

async def download_image(session, url, path):
    async with SEM:
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                print(f"[DOWNLOAD] {url}")
                async with session.get(
                    url,
                    headers={"X-Api-Key": API_KEY},
                    timeout=aiohttp.ClientTimeout(total=90)
                ) as resp:
                    print(f"[IMG STATUS] {resp.status}")
                    resp.raise_for_status()
                    data = await resp.read()

                async with aiofiles.open(path, "wb") as f:
                    await f.write(data)

                print(f"[SAVED] {path}")
                return
            except Exception as e:
                print(f"[IMG ERROR] {e}")
                if attempt == MAX_RETRIES:
                    print(f"[FAILED] {path}")
                    return
                await asyncio.sleep(attempt * 2)

async def scrape_all_cards():
    if not API_KEY:
        raise RuntimeError("POKEMONTCG_API_KEY not set")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    async with aiohttp.ClientSession() as session:
        total_downloaded = 0

        # Loop letters A–Z
        for letter in "abcdefghijklmnopqrstuvwxyz":
            q = f"name:{letter}*"
            page = 1
            print(f"\n[LETTER] {letter.upper()}")

            while True:
                data = await fetch_cards_page(session, q, page)
                if not data:
                    break

                cards = data.get("data", [])
                print(f"[PAGE] {page} count={len(cards)}")
                if not cards:
                    break

                tasks = []
                for card in cards:
                    try:
                        set_name = sanitize(card["set"]["name"])
                        card_name = sanitize(card["name"])
                        number = sanitize(card["number"])
                        image_url = card["images"]["small"]

                        set_dir = os.path.join(OUTPUT_DIR, set_name)
                        os.makedirs(set_dir, exist_ok=True)

                        filename = f"{card_name}_{number}.png"
                        filepath = os.path.join(set_dir, filename)

                        if os.path.exists(filepath):
                            print(f"[SKIP] {filename}")
                            continue

                        tasks.append(download_image(session, image_url, filepath))
                        total_downloaded += 1
                    except Exception as e:
                        print(f"[CARD ERROR] {e}")

                if tasks:
                    await asyncio.gather(*tasks)

                page += 1
                await asyncio.sleep(PAGE_DELAY)

        print(f"\n[DONE] Total images processed: {total_downloaded}")

if __name__ == "__main__":
    asyncio.run(scrape_all_cards())
