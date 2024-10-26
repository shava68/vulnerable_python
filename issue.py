import logging
import sqlite3
from Crypto.Cipher import DES
import ssl
import socket
import subprocess  # Для выполнения команд ОС

# Настройка логирования для SQL-инъекции
logging.basicConfig(filename='application.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Уязвимость 1: Использование устаревшего алгоритма DES
def encrypt_data(data):
    key = b'12345678'  # DES использует 8-байтный ключ
    cipher = DES.new(key, DES.MODE_ECB)  # Уязвимость 2: Использование небезопасного режима ECB
    padded_data = data.ljust(8).encode('utf-8')  # Дополняем данные до 8 байт
    encrypted_data = cipher.encrypt(padded_data)
    return encrypted_data

# Уязвимость 3: Отключение проверки сертификатов SSL/TLS
def connect_to_server(host, port):
    context = ssl._create_unverified_context()  # Отключение проверки сертификата
    with socket.create_connection((host, port)) as sock:
        with context.wrap_socket(sock, server_hostname=host) as ssock:
            # Сертификат сервера больше не логируется
            pass

# Уязвимость 4: SQL-инъекция
def get_user_data(user_id):
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()

    # Уязвимость: SQL-инъекция, строка не параметризована
    query = f"SELECT * FROM users WHERE id = '{user_id}'"
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            logging.info(f"User ID: {row[0]}, Username: {row[1]}")  # Только это логгирование оставлено
    except Exception as e:
        # Логирование ошибки с трассировкой стека
        logging.error(f"Error occurred: {e}")
        raise e

    conn.close()

# Уязвимость 5: Инъекция команд ОС через ping
def ping_host(ip):
    try:
        # Уязвимость: выполнение пользовательской команды напрямую без фильтрации
        command = f"ping -c 4 {ip}"
        result = subprocess.check_output(command, shell=True, text=True)
        # Логгирования больше нет
        print(f"Ping result:\n{result}")
    except subprocess.CalledProcessError as e:
        # Больше не логируем ошибку, только выводим ее в консоль
        print(f"Error executing command: {e}")
        raise e

if name == "main":
    # Уязвимый процесс шифрования данных
    sensitive_data = "SensitiveData"
    encrypted = encrypt_data(sensitive_data)
    print(f"Encrypted data (DES-ECB): {encrypted}")

    # Подключение к серверу с уязвимостью в проверке сертификата
    host = "example.com"
    port = 443
    connect_to_server(host, port)

    # Пример SQL-инъекции
    user_id = input("Enter user ID for SQL Injection: ")
    get_user_data(user_id)

    # Пример инъекции команд ОС через ввод IP для ping
    ip = input("Enter IP address to ping (Command Injection possible): ")
    ping_host(ip)