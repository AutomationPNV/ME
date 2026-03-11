from fastapi import APIRouter, HTTPException, Form
from database.connection import get_db_connection
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/motors", tags=["motors"])

@router.put("/{motor_id}")
async def update_motor(
    motor_id: int,
    motor_name_text: str = Form(...),
    ip_tesys_text: str = Form(...),
    ip_plc_text: str = Form(...),
    motor_location_text: str = Form(...)
):
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
        
        # Оновлюємо мотор
        cur.execute("""
            UPDATE motors_list 
            SET name_motors = %s, ip_tesys = %s, ip_plc = %s, location = %s
            WHERE id = %s
        """, (motor_name_text, ip_tesys_text, ip_plc_text, motor_location_text, motor_id))
        
        conn.commit()
        cur.close()
        
        return JSONResponse(
            status_code=200,
            content={"message": f"Мотор з ID {motor_id} успішно оновлено"}
        )
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
