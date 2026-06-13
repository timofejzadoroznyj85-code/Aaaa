import aiohttp
from config import PIARFLOW_API_KEY, PIARFLOW_BASE_URL

HEADERS = {"Authorization": f"Bearer {PIARFLOW_API_KEY}"}

async def get_sponsors(user_id, chat_id, max_sponsors=3):
    async with aiohttp.ClientSession() as s:
        r = await s.post(
            f"{PIARFLOW_BASE_URL}/sponsors",
            headers=HEADERS,
            json={"user_id": user_id, "chat_id": chat_id, "max_sponsors": max_sponsors}
        )
        return await r.json()


async def check_sponsors(user_id, links):
    async with aiohttp.ClientSession() as s:
        r = await s.post(
            f"{PIARFLOW_BASE_URL}/sponsors/check",
            headers=HEADERS,
            json={"user_id": user_id, "links": links}
        )
        return await r.json()
