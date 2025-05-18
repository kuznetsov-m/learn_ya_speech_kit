import os
from datetime import datetime
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters, CommandHandler
from dotenv import load_dotenv
from pydub import AudioSegment
import tempfile

# Загружаем переменные окружения из файла .env
load_dotenv()

# Получаем токен бота из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("Не указан токен бота. Создайте файл .env и добавьте в него BOT_TOKEN=ваш_токен")

# Создаем директорию для сохранения аудио, если её нет
AUDIO_DIR = 'received_audio'
os.makedirs(AUDIO_DIR, exist_ok=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет приветственное сообщение."""
    await update.message.reply_text(
        'Привет! Отправь мне голосовое сообщение или аудиофайл, и я сохраню его в формате WAV.'
    )

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает полученные аудио файлы и конвертирует их в WAV."""
    try:
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
            
            # Создаем имя для WAV файла
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            wav_filename = f'audio_{timestamp}.wav'
            wav_filepath = os.path.join(AUDIO_DIR, wav_filename)

            # Конвертируем в WAV
            audio = AudioSegment.from_file(temp_original.name, format=original_format)
            audio.export(wav_filepath, format='wav')

            # Удаляем временный файл
            os.unlink(temp_original.name)

        # Отправляем подтверждение
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