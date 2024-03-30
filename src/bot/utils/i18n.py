from config import conf
import json
import aiohttp


DEEP_API_URL = "https://api-free.deepl.com/v2/translate"
headers = {
    "Authorization": "DeepL-Auth-Key " + conf.DEEPL_API_TOKEN,
    "Content-Type": "application/json",
}


class TranslationError(Exception):
    pass


async def translate_request(text: str, source_lang: str, target_lang: str):
    async with aiohttp.ClientSession(headers=headers) as session:
        response = await session.post(
            url=DEEP_API_URL,
            data=json.dumps(
                {
                    "text": [text],
                    "source_lang": source_lang,
                    "target_lang": target_lang,
                }
            ),
        )
        if response.status == 200:
            response_data = await response.json()
            return response_data.get("translations")[0].get("text")
        else:
            raise TranslationError(await response.read())
