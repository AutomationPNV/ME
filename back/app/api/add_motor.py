from fastapi import APIRouter, HTTPException, Form
from database.connection import get_db_connection
from fastapi.responses import JSONResponse


router = APIRouter(prefix="/api/add_motor", tags=["motors"])

# Додати новий мотор
@router.post("/")
async def add_motor(
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
        
        # Перевіряємо, чи існує таблиця
        cur.execute("""
            INSERT INTO motors_list (name_motors, ip_tesys, ip_plc, location)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (motor_name_text, ip_tesys_text, ip_plc_text, motor_location_text))
        
        motor_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        
        return JSONResponse(
            status_code=201,
            content={"message": f"Мотор з ID {motor_id} успішно додано", "id": motor_id}
        )
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

