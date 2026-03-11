from fastapi import APIRouter, HTTPException
from database.connection import get_db_connection
from schemas.schemas_motor import Motor
from typing import List

router = APIRouter(prefix="/api/motors", tags=["motors"])

@router.get("/", response_model=List[Motor])
async def get_motors():
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Не вдалося підключитися до БД")
    
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, name_motors, ip_tesys, ip_plc, location FROM motors_list ORDER BY id DESC")
        rows = cur.fetchall()
        cur.close()
        
        motors = []
        for row in rows:
            motors.append({
                "id": row[0],
                "name_motors": row[1],
                "ip_tesys": row[2],
                "ip_plc": row[3],
                "location": row[4],
                "status": "active"  # Можна додати логіку для статусу
            })
        
        return motors
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
