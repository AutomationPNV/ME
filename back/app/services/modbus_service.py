from pymodbus.client import ModbusTcpClient
import taos
from datetime import datetime
import time
import threading
import logging
import os

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Підключення до TDengine
def get_tdengine_connection():
    try:
        conn = taos.connect(
            host=os.getenv('TDENGINE_HOST', 'tdengine'),
            user=os.getenv('TDENGINE_USER', 'root'),
            password=os.getenv('TDENGINE_PASSWORD', 'taosdata'),
            database=os.getenv('TDENGINE_DB', 'motor_monitoring')
        )
        return conn
    except Exception as e:
        logger.error(f"❌ Помилка підключення до TDengine: {e}")
        return None

# Ініціалізація бази даних та супертаблиці
def init_tdengine():
    conn = get_tdengine_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Створюємо базу даних, якщо не існує
        cursor.execute("CREATE DATABASE IF NOT EXISTS motor_monitoring INTERVAL 1h")
        cursor.execute("USE motor_monitoring")
        
        # Створюємо супертаблицю
        cursor.execute("""
            CREATE STABLE IF NOT EXISTS motor_metrics (
                ts TIMESTAMP,
                frequency FLOAT,
                voltage_avg FLOAT,
                voltage_unbalance FLOAT,
                cos_phi FLOAT,
                phase_unbalance FLOAT,
                current_l1 FLOAT,
                current_l2 FLOAT,
                current_l3 FLOAT,
                vibration FLOAT
            ) TAGS (
                motor_name BINARY(100),
                tesys_ip BINARY(50)
            )
        """)
        
        cursor.close()
        conn.close()
        logger.info("✅ TDengine ініціалізовано успішно")
        return True
    except Exception as e:
        logger.error(f"❌ Помилка ініціалізації TDengine: {e}")
        return False

# Функція для читання даних з Modbus
def read_motor_data_modbus(ip_tesys: str, motor_name: str, device_id: int = 1) -> dict:
    client = ModbusTcpClient(ip_tesys, port=502, timeout=3)
    if not client.connect():
        logger.error(f"❌ Не вдалося підключитися до {ip_tesys} ({motor_name})")
        return None

    data = {
        "motor_name": motor_name,
        "tesys_ip": ip_tesys,
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        # Частота (регістр 474, 2 слова)
        res_freq = client.read_holding_registers(address=474, count=2, device_id=device_id)
        if not res_freq.isError() and res_freq.registers:
            # 32-бітне значення (Big Endian)
            freq_raw = (res_freq.registers[0] << 16) | res_freq.registers[1]
            data["frequency"] = round(freq_raw / 10.0, 2)
        else:
            data["frequency"] = 0.0

        # Середня напруга (регістр 476, 2 слова)
        res_volt = client.read_holding_registers(address=476, count=2, device_id=device_id)
        if not res_volt.isError() and res_volt.registers:
            volt_raw = (res_volt.registers[0] << 16) | res_volt.registers[1]
            data["voltage_avg"] = round(volt_raw / 10.0, 2)
        else:
            data["voltage_avg"] = 0.0

        # Дизбаланс напруги (регістр 480, 2 слова)
        res_vimb = client.read_holding_registers(address=480, count=2, device_id=device_id)
        if not res_vimb.isError() and res_vimb.registers:
            vimb_raw = (res_vimb.registers[0] << 16) | res_vimb.registers[1]
            data["voltage_unbalance"] = round(vimb_raw / 10.0, 2)
        else:
            data["voltage_unbalance"] = 0.0

        # cos φ (регістр 481, 1 слово)
        res_pf = client.read_holding_registers(address=481, count=1, device_id=device_id)
        if not res_pf.isError() and res_pf.registers:
            data["cos_phi"] = round(res_pf.registers[0] / 100.0, 2)
        else:
            data["cos_phi"] = 0.0

        # Дизбаланс фаз (регістр 471, 1 слово)
        res_phase = client.read_holding_registers(address=471, count=1, device_id=device_id)
        if not res_phase.isError() and res_phase.registers:
            data["phase_unbalance"] = round(res_phase.registers[0] / 10.0, 2)
        else:
            data["phase_unbalance"] = 0.0

        # Струми фаз
        # L1 (регістр 501)
        res_l1 = client.read_holding_registers(address=501, count=1, device_id=device_id)
        if not res_l1.isError() and res_l1.registers:
            data["current_l1"] = round(res_l1.registers[0] * 0.01, 2)
        else:
            data["current_l1"] = 0.0

        # L2 (регістр 503)
        res_l2 = client.read_holding_registers(address=503, count=1, device_id=device_id)
        if not res_l2.isError() and res_l2.registers:
            data["current_l2"] = round(res_l2.registers[0] * 0.01, 2)
        else:
            data["current_l2"] = 0.0

        # L3 (регістр 505)
        res_l3 = client.read_holding_registers(address=505, count=1, device_id=device_id)
        if not res_l3.isError() and res_l3.registers:
            data["current_l3"] = round(res_l3.registers[0] * 0.01, 2)
        else:
            data["current_l3"] = 0.0

        # Вібрація (можна додати окремий регістр, якщо є)
        # Приклад: регістр 490 для вібрації
        res_vib = client.read_holding_registers(address=490, count=1, device_id=device_id)
        if not res_vib.isError() and res_vib.registers:
            data["vibration"] = round(res_vib.registers[0] / 1000.0, 3)
        else:
            data["vibration"] = 0.0

        logger.info(f"✅ Дані отримано з {motor_name} ({ip_tesys})")
        return data

    except Exception as e:
        logger.error(f"❌ Помилка читання з {ip_tesys} ({motor_name}): {e}")
        return None
    finally:
        client.close()

# Функція для збереження даних в TDengine
def save_to_tdengine(data: dict):
    if not data:
        return False
    
    conn = get_tdengine_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("USE motor_monitoring")
        
        # Вставляємо дані
        cursor.execute("""
            INSERT INTO motor_metrics 
            USING motor_metrics TAGS(?, ?) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['motor_name'],           # tag: motor_name
            data['tesys_ip'],              # tag: tesys_ip
            data['timestamp'],              # ts
            data.get('frequency', 0.0),     # frequency
            data.get('voltage_avg', 0.0),    # voltage_avg
            data.get('voltage_unbalance', 0.0), # voltage_unbalance
            data.get('cos_phi', 0.0),        # cos_phi
            data.get('phase_unbalance', 0.0), # phase_unbalance
            data.get('current_l1', 0.0),     # current_l1
            data.get('current_l2', 0.0),     # current_l2
            data.get('current_l3', 0.0),     # current_l3
            data.get('vibration', 0.0)       # vibration
        ))
        
        cursor.close()
        conn.close()
        logger.info(f"💾 Дані для {data['motor_name']} збережено в TDengine")
        return True
        
    except Exception as e:
        logger.error(f"❌ Помилка збереження в TDengine: {e}")
        return False

# Функція для отримання списку моторів з PostgreSQL
def get_motors_from_postgres():
    import psycopg2
    import os
    
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'db'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('POSTGRES_DB', 'motors'),
            user=os.getenv('POSTGRES_USER', 'admin'),
            password=os.getenv('POSTGRES_PASSWORD', 'admin')
        )
        cursor = conn.cursor()
        cursor.execute("SELECT name_motors, ip_tesys FROM motors_list")
        motors = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [{"name": m[0], "ip": m[1]} for m in motors]
    except Exception as e:
        logger.error(f"❌ Помилка отримання моторів з PostgreSQL: {e}")
        return []

# Головна функція збору даних
def collect_all_motors_data():
    logger.info("🔄 Початок збору даних з усіх моторів...")
    
    motors = get_motors_from_postgres()
    if not motors:
        logger.warning("⚠️ Немає моторів для збору даних")
        return
    
    for motor in motors:
        data = read_motor_data_modbus(motor['ip'], motor['name'])
        if data:
            save_to_tdengine(data)
        time.sleep(1)  # Невелика затримка між запитами до різних моторів
    
    logger.info("✅ Збір даних завершено")

# Фоновий потік для періодичного збору даних
class ModbusCollectorThread(threading.Thread):
    def __init__(self, interval_seconds=15):
        super().__init__()
        self.interval = interval_seconds
        self.running = True
        self.daemon = True  # Потік завершиться при зупинці основної програми
    
    def stop(self):
        self.running = False
    
    def run(self):
        logger.info(f"🚀 Запуск ModbusCollectorThread з інтервалом {self.interval} секунд")
        
        # Ініціалізація TDengine
        init_tdengine()
        
        while self.running:
            try:
                collect_all_motors_data()
                
                # Чекаємо наступного циклу
                for _ in range(self.interval):
                    if not self.running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"❌ Помилка в потоці збору даних: {e}")
                time.sleep(5)  # Пауза перед повторною спробою