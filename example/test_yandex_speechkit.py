from argparse import ArgumentParser
from speechkit import model_repository, configure_credentials, creds
from speechkit.stt import AudioProcessingType
import json

# Загружаем API-ключ из файла
with open('key.json', 'r') as f:
    key_data = json.load(f)

# Аутентификация через API-ключ.
configure_credentials(
    yandex_credentials=creds.YandexCredentials(api_key=key_data['key'])
)

def recognize(audio):
   model = model_repository.recognition_model()

   # Задайте настройки распознавания.
   model.model = 'general'
   model.language = 'ru-RU'
   model.audio_processing_type = AudioProcessingType.Full

   # Распознавание речи в указанном аудиофайле и вывод результатов в консоль.
   result = model.transcribe_file(audio)
   
   # Сохраняем нормализованный текст в файл
   with open('norm_text.txt', 'w', encoding='utf-8') as f:
      for res in result:
         f.write(res.normalized_text + '\n')
   
   # Выводим результаты в консоль
   for c, res in enumerate(result):
      print('=' * 80)
      print(f'channel: {c}\n\nraw_text:\n{res.raw_text}\n\nnorm_text:\n{res.normalized_text}\n')
      if res.has_utterances():
         print('utterances:')
         for utterance in res.utterances:
            print(utterance)
   
   print(f"\nНормализованный текст сохранен в файл 'norm_text.txt'")

if __name__ == '__main__':
   parser = ArgumentParser()
   parser.add_argument('--audio', type=str, help='audio path', required=True)

   args = parser.parse_args()

   recognize(args.audio)
