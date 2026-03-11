from fastapi import APIRouter, HTTPException
from database.connection import get_db_connection
from fastapi.responses import JSONResponse


router = APIRouter(prefix="/api/delete_motor", tags=["motors"])

@router.delete("/{motor_id}")
async def delete_motor(motor_id: int):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Не вдалося підключитися до БД")
    
    try:
        cur = conn.cursor()
        
        # Перевіряємо, чи існує мотор
        cur.execute("SELECT id FROM motors_list WHERE id = %s", (motor_id,))
        motor = cur.fetchone()
        
        if not motor:
            raise HTTPException(status_code=404, detail=f"Мотор з ID {motor_id} не знайдено")
        
        # Видаляємо мотор
        cur.execute("DELETE FROM motors_list WHERE id = %s", (motor_id,))
        
        # Після видалення перевіряємо, чи залишились мотори
        cur.execute("SELECT COUNT(*) FROM motors_list")
        count = cur.fetchone()[0]
        
        # Якщо моторів більше немає, скидаємо sequence
        if count == 0:
            print("🔄 Моторів не залишилось, скидаємо sequence...")
            cur.execute("ALTER SEQUENCE motors_list_id_seq RESTART WITH 1")
            print("✅ Sequence скинуто")
        else:
            # Якщо мотори є, але ми хочемо компактні ID,
            # можна перерахувати всі ID заново (опціонально)
            # Це складніша операція, краще використовувати тільки при потребі
            pass
            
        conn.commit()
        cur.close()
        
        # Отримуємо оновлений список моторів для відповіді
        cur = conn.cursor()
        cur.execute("SELECT id, name_motors, ip_tesys, ip_plc, location FROM motors_list ORDER BY id")
        updated_motors = cur.fetchall()
        cur.close()
        
        return JSONResponse(
            status_code=200,
            content={
                "message": f"Мотор з ID {motor_id} успішно видалено",
                "motors_count": count,
                "motors": [
                    {
                        "id": m[0],
                        "name_motors": m[1],
                        "ip_tesys": m[2],
                        "ip_plc": m[3],
                        "location": m[4]
                    } for m in updated_motors
                ]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()