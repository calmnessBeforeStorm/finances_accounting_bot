# Telegram Bot for Financial Tracking

Этот проект представляет собой Telegram-бота для учета финансов, работающего на Python 3.8.10 с использованием Aiogram и Firebase для хранения данных.

## 📌 Установка и запуск

1. **Создайте виртуальное окружение:**
   ```sh
   python3 -m venv venv
   ```
2. **Активируйте виртуальное окружение:**
   - Windows:
     ```sh
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```sh
     source venv/bin/activate
     ```
3. **Установите зависимости:**
   ```sh
   pip install -r requirements.txt
   ```
4. **Создайте файл `_config.py`** (он игнорируется в `.gitignore`) с содержимым:
   ```python
   BOT_TOKEN = "ВАШ_TELEGRAM_ТОКЕН"
   FIREBASE_CRED = {
       "type": "service_account",
       "project_id": "ВАШ_PROJECT_ID",
       "private_key_id": "ВАШ_PRIVATE_KEY_ID",
       "private_key": "ВАШ_PRIVATE_KEY",
       "client_email": "ВАШ_CLIENT_EMAIL",
       "client_id": "ВАШ_CLIENT_ID",
       "auth_uri": "https://accounts.google.com/o/oauth2/auth",
       "token_uri": "https://oauth2.googleapis.com/token",
       "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
       "client_x509_cert_url": "ВАШ_CLIENT_CERT_URL"
   }
   ```
   **Важно!** В переменной `FIREBASE_CRED` должны быть **не путь к файлу**, а **сами данные**, как в JSON-файле Firebase, который скачивается при настройке ключей.

5. **Запустите бота:**
   ```sh
   python main.py
   ```

## 📂 Структура проекта

- `main.py` – инициализация и запуск бота.
- `FIREBASE.py` – подключение к Firebase и управление базой данных.
- `_config.py` – содержит токен бота и учетные данные Firebase (игнорируется в Git).
- `requirements.txt` – список зависимостей для установки.

## 🔗 Используемые технологии
- Python 3.8.10
- Aiogram 3+
- Firebase Firestore
- Virtualenv

## 🚀 Функционал бота
- Добавление и удаление банковских счетов
- Отображение всех счетов и их баланса
- Добавление и удаление долгов
- Просмотр списка долгов и общей суммы
- Удобные команды для работы с ботом

## 📝 Лицензия
Этот проект разработан для личного использования. Свободно модифицируйте и улучшайте его под свои нужды.

---
🔥 Удачного использования! Если есть вопросы, не стесняйтесь их задавать.

