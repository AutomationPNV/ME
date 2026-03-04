from fastapi import APIRouter, Request, Form
from models import AddMotor
import psycopg2

add = APIRouter()

conn = psycopg2.connect(
    host='localhost',  
    port=5532,         
    database='motor_db',
    user='admin',
    password='0000'
)


@add.post('/add_motor')
async def add_motor(
    request: Request,
    motor_name_text: str = Form(...),
    ip_tesys_text:str = Form(...),
    ip_plc_text:str = Form(...),
    motor_location_text:str = Form(...)):

    new_motor = AddMotor(
        name_motor = motor_name_text,
        ip_tesys = ip_tesys_text,
        ip_plc=ip_plc_text,
        location=motor_location_text
    )

    

    insert_query = """
        INSERT INTO motors_list (name_motors, ip_tesys, ip_plc, location)
        VALUES (%s, %s, %s, %s)
        RETURNING id;
    """
    cur = conn.cursor()
    cur.execute(insert_query, (motor_name_text, ip_tesys_text, ip_plc_text, motor_location_text))
    conn.commit()


    motor_id = cur.fetchone()[0]
    cur.close()
    
    return {"message": f"Додано новий мотор з id: {motor_id}"}