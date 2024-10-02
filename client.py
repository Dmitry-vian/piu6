import socket
import time
import json
import random
import logging
from datetime import datetime
import os

# Настройка логирования
log_directory = 'logs'
os.makedirs(log_directory, exist_ok=True)  # Создаем директорию для логов, если её нет

# Генерируем уникальное имя файла с временной меткой
log_filename = datetime.now().strftime('tcp_server_%Y-%m-%d_%H-%M-%S.log')

# Настройка логирования
logging.basicConfig(
    filename=os.path.join(log_directory, log_filename),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Параметры подключения
HOST = '80.87.107.167'  # IP-адрес ППО
PORT = 6000  # Порт для подключения


def generate_uav_data(packet_type):
    """
    Генерация случайных данных о БПЛА в зависимости от типа пакета.

    :param packet_type: Тип пакета (int), определяющий формат данных.
    :return: Словарь с данными о БПЛА, соответствующими переданному типу пакета.
    """
    if packet_type == 2:
        return {
            "packetType": 1,
            "deviceType": 1,
            "deviceLatitude": round(random.uniform(-90.0, 90.0), 6),
            "deviceLongitude": round(random.uniform(-180.0, 180.0), 6),
            "deviceAltitude": random.uniform(100, 500),
            "signalType": random.choice([1, 2, 3]),
            "signalFrequency": random.randint(2400000, 6000000),
            "signalAmplitude": random.randint(-150, 20),
            "signalWidth": random.randint(1000, 2000),
            "signalDetectionType": random.choice([1, 2]),
            "uav": {
                "uavType": "DJI",
                "serialNumber": str(random.randint(1000000, 9999999)),
                "startUavLatitude": round(random.uniform(-90.0, 90.0), 6),
                "startUavLongitude": round(random.uniform(-180.0, 180.0), 6),
                "uavLatitude": round(random.uniform(-90.0, 90.0), 6),
                "uavLongitude": round(random.uniform(-180.0, 180.0), 6),
                "uavAltitude": random.uniform(100, 500),
                "operatorLatitude": round(random.uniform(-90.0, 90.0), 6),
                "operatorLongitude": round(random.uniform(-180.0, 180.0), 6)
            }
        }

    elif packet_type == 3:
        return {
            "packetType": 3,
            "deviceType": 1,
        }

    elif packet_type == 4:
        return {
            "packetType": 4,
            "deviceType": random.randint(1, 5),
            "deviceStatus": random.choice([1, 2, 3]),
            "supressMode": random.randint(0, 1),
            "params": [
                {
                    "centerFrequency": random.randint(100000000, 600000000),
                    "receiveSensitivity": random.randint(0, 30),
                    "detectionBandwidth": random.randint(10000, 50000),
                    "idents": [
                        {
                            "signalType": random.choice(["TypeA", "TypeB"]),
                            "signalDetectionType": random.choice(["DetectionA", "DetectionB"]),
                        }
                    ]
                }
            ],
            "additional": "Дополнительная информация"
        }

    elif packet_type == 20:
        error_status = random.randint(1, 4)
        error_comment = {
            1: "Не влияет на функционирование устройства.",
            2: "Частичный отказ аппаратных элементов устройства.",
            3: "Полный отказ аппаратных элементов устройства.",
            4: "Устройство не выполняет свои функции."
        }[error_status]

        return {
            "time": int(time.time_ns()),  # GPS время [наносекунды]
            "packetType": 20,
            "deviceID": random.randint(1, 10),
            "deviceType": random.randint(1, 5),
            "deviceErrorStatus": error_status,
            "deviceErrorComment": error_comment
        }

    else:
        return {}


def connect_to_ppo():
    """
    Устанавливает соединение с ППО и обрабатывает данные.

    Запускает цикл, в котором происходит попытка подключения к ППО.
    При успешном подключении, принимает данные и генерирует случайные
    данные о БПЛА для отправки. В случае ошибок, повторяет попытку
    подключения с задержкой.
    """
    while True:
        try:
            # Установка соединения с ППО
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, PORT))
                logging.info("Подключение к ППО успешно")
                print("Подключение к ППО успешно")

                while True:
                    data = s.recv(1024).decode('utf-8')
                    if not data:
                        break  # Прерывание цикла при отсутствии данных
                    packet_type = json.loads(data).get('packetType')
                    logging.info(f"Получено от ППО: {data}")

                    # Генерация случайных данных о БПЛА
                    uav_data = generate_uav_data(packet_type)
                    s.sendall(json.dumps(uav_data).encode('utf-8'))
                    logging.info(f"Отправлено на ППО: {json.dumps(uav_data)}")

                    # Отправка данных с интервалом 3-7 секунд
                    time.sleep(3)

        except ConnectionRefusedError:
            logging.error("Подключение отклонено, повторная попытка через 5 секунд...")
            print("Подключение отклонено, повторная попытка через 5 секунд...")
            time.sleep(5)

        except OSError as e:
            logging.error(f"Ошибка сокета: {e}")
            time.sleep(5)

        except Exception as e:
            logging.error(f"Неожиданная ошибка: {e}")
            time.sleep(5)


if __name__ == '__main__':
    connect_to_ppo()
