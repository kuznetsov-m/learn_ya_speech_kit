# source: https://github.com/allseeteam/yandexgpt-python

from yandex_gpt import YandexGPT, YandexGPTConfigManagerForAPIKey

# Setup configuration (input fields may be empty if they are set in environment variables)
config = YandexGPTConfigManagerForAPIKey(model_type="yandexgpt", catalog_id="your_catalog_id", api_key="your_api_key")

# Instantiate YandexGPT
yandex_gpt = YandexGPT(config_manager=config)

# Async function to get completion
async def get_completion():
    messages = [{"role": "user", "text": "Hello, world!"}]
    completion = await yandex_gpt.get_async_completion(messages=messages)
    print(completion)

# Run the async function
import asyncio
asyncio.run(get_completion())