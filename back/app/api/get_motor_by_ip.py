from fastapi import APIRouter, HTTPException
from database.connection import get_db_connection

router = APIRouter(prefix="/api/motors", tags=["motors"])


@router.get("/{motor_id}")
async def get_motor(motor_id: int):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Не вдалося підключитися до БД")
    
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, name_motors, ip_tesys, ip_plc, location FROM motors_list WHERE id = %s", (motor_id,))
        row = cur.fetchone()
        cur.close()
        
        if not row:
            raise HTTPException(status_code=404, detail=f"Мотор з ID {motor_id} не знайдено")
        
        return {
            "id": row[0],
            "name_motors": row[1],
            "ip_tesys": row[2],
            "ip_plc": row[3],
            "location": row[4],
            "status": "active"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
