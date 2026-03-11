from database.connection import get_db_connection

def init_db():
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            # Створюємо таблицю, якщо вона не існує
            cur.execute("""
                CREATE TABLE IF NOT EXISTS motors_list (
                    id SERIAL PRIMARY KEY,
                    name_motors VARCHAR(255) NOT NULL,
                    ip_tesys VARCHAR(50),
                    ip_plc VARCHAR(50),
                    location VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            cur.close()
            print("Таблиця motors_list успішно створена або вже існує")
        except Exception as e:
            print(f"Помилка створення таблиці: {e}")
        finally:
            conn.close()
