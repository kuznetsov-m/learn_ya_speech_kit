import os
from datetime import datetime
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters, CommandHandler
from dotenv import load_dotenv
from pydub import AudioSegment
import tempfile
from speechkit import model_repository, configure_credentials, creds
from speechkit.stt import AudioProcessingType

# Загружаем переменные окружения из файла .env
load_dotenv()

# Получаем токен бота из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')
YANDEX_API_KEY = os.getenv('YANDEX_API_KEY')

if not BOT_TOKEN:
    raise ValueError("Не указан токен бота. Создайте файл .env и добавьте в него BOT_TOKEN=ваш_токен")
if not YANDEX_API_KEY:
    raise ValueError("Не указан API ключ Яндекса. Добавьте в файл .env строку YANDEX_API_KEY=ваш_ключ")

# Настраиваем Yandex SpeechKit
configure_credentials(
    yandex_credentials=creds.YandexCredentials(api_key=YANDEX_API_KEY)
)

# Создаем директорию для сохранения аудио и текста, если её нет
AUDIO_DIR = 'received_audio'
TEXT_DIR = 'transcribed_text'
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(TEXT_DIR, exist_ok=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет приветственное сообщение."""
    await update.message.reply_text(
        'Привет! Отправь мне голосовое сообщение или аудиофайл, и я сохраню его в формате WAV и сделаю транскрибацию.'
    )

async def transcribe_audio(wav_filepath):
    """Транскрибирует аудио файл с помощью Yandex SpeechKit."""
    model = model_repository.recognition_model()
    model.model = 'general'
    model.language = 'ru-RU'
    model.audio_processing_type = AudioProcessingType.Full

    result = model.transcribe_file(wav_filepath)
    # Собираем только нормализованный текст из всех частей
    transcribed_text = ' '.join(res.normalized_text for res in result)
    return transcribed_text

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает полученные аудио файлы, конвертирует их в WAV и делает транскрибацию."""
    try:
        await update.message.reply_text('Обработка аудио...')
        
        # Получаем ID чата
        chat_id = update.effective_chat.id
        
        # Получаем файл
        if update.message.voice:
            file = await update.message.voice.get_file()
            original_format = 'ogg'  # Голосовые сообщения приходят в формате .ogg
        elif update.message.audio:
            file = await update.message.audio.get_file()
            original_format = update.message.audio.file_name.split('.')[-1]
        else:
            return

        # Создаем временный файл для исходного аудио
        with tempfile.NamedTemporaryFile(suffix=f'.{original_format}', delete=False) as temp_original:
            # Скачиваем файл во временный файл
            await file.download_to_drive(temp_original.name)
            
            # Создаем имя для WAV файла с ID чата
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            wav_filename = f'audio_{chat_id}_{timestamp}.wav'
            wav_filepath = os.path.join(AUDIO_DIR, wav_filename)

            # Конвертируем в WAV
            audio = AudioSegment.from_file(temp_original.name, format=original_format)
            audio.export(wav_filepath, format='wav')

            # Удаляем временный файл
            os.unlink(temp_original.name)

        # Транскрибируем аудио
        await update.message.reply_text('Выполняется транскрибация...')
        transcribed_text = await transcribe_audio(wav_filepath)

        # Сохраняем текст в файл с ID чата
        text_filename = f'text_{chat_id}_{timestamp}.txt'
        text_filepath = os.path.join(TEXT_DIR, text_filename)
        with open(text_filepath, 'w', encoding='utf-8') as f:
            f.write(transcribed_text)

        # Отправляем результат
        await update.message.reply_text(f'Транскрибация:\n\n{transcribed_text}')
        await update.message.reply_text('готово')

    except Exception as e:
        await update.message.reply_text(f'Произошла ошибка при обработке аудио: {str(e)}')
        raise

def main():
    """Запускает бота."""
    # Создаем приложение с токеном из переменных окружения
    application = Application.builder().token(BOT_TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, handle_audio))

    # Запускаем бота
    print("Бот запущен. Нажмите Ctrl+C для остановки.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main() 