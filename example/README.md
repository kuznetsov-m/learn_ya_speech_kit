Документация: https://yandex.cloud/ru/docs/speechkit/sdk/python/request

как запускать:
python3 test.py --audio speech.pcm

результат:
```
raw_text:
я буду я буду пробовать писать программу тестовую для работы с яндекс спичкит в целом идея работы с яндекс спичкит мне пришла когда мы сидели в кафе

norm_text:
Я буду. Я буду пробовать писать программу тестовую для работы с Яндекс Спичкит в целом идея. Работы с Яндекс Спичкит мне пришла. Когда мы сидели в кафе?

utterances:
- Я буду. [0.220, 0.520]
- Я буду пробовать писать программу тестовую для работы с Яндекс Спичкит в целом идея. [3.340, 11.269]
- Работы с Яндекс Спичкит мне пришла. [12.840, 16.100]
- Когда мы сидели в кафе? [17.760, 20.080]
```

как конвертировать m4a -> wav:
ffmpeg -i 15s.m4a -acodec pcm_s16le -ar 16000 15s.wav