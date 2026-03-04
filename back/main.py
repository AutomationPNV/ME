import psycopg2
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os

from api.add_motors import add as add_motor_router

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)

templates = Jinja2Templates(directory=os.path.join(ROOT_DIR, 'front', 'templates'))
app.include_router(add_motor_router)    

conn = psycopg2.connect(
    host='localhost',  
    port=5532,         
    database='motor_db',
    user='admin',
    password='0000'
)

app.mount(
    '/static',
    StaticFiles(directory=os.path.join(ROOT_DIR, 'front')), 
    name='static'
)

@app.get('/', response_class=HTMLResponse)
async def root(request: Request):
    cur = conn.cursor()

    cur.execute("SELECT * FROM motors_list ORDER BY id ASC LIMIT 5;")
    motors = cur.fetchall()

    cur.close()

    motors_dict =[
        {
            "id": motor[0],
            "name_motor": motor[1],
            "ip_tesys": motor[2],
            "ip_plc": motor[3],
            "location": motor[4]
        }
         for motor in motors
    ]

    return templates.TemplateResponse(
        "index.html",{"request": request, 'motors': motors_dict})




   
