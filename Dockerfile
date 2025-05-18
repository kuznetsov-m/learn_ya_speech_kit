FROM python:3.10-slim

# Установка ffmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Копирование файлов зависимостей
COPY requirements.txt .

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY audio_bot.py .

# Создание директорий для сохранения файлов
RUN mkdir -p received_audio transcribed_text

# Запуск бота
CMD ["python", "audio_bot.py"] 