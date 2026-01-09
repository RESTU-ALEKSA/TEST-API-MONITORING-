from fastapi import FastAPI
import mysql.connector
import os
from dotenv import load_dotenv

# Load .env saat lokal
load_dotenv()

app = FastAPI(title="Smart Farm Health Monitoring API")

def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

# ================================
# POST DATA SENSOR (ESP32)
# ================================
@app.post("/sensor")
def insert_sensor(ph_value: float, soil_moisture: int):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    query = """
    INSERT INTO sensor_data (ph_value, soil_moisture)
    VALUES (%s, %s)
    """
    cursor.execute(query, (ph_value, soil_moisture))
    db.commit()

    cursor.close()
    db.close()

    return {"message": "Data sensor berhasil disimpan"}

# ================================
# GET DATA SENSOR TERAKHIR
# ================================
@app.get("/sensor/latest")
def get_latest_sensor():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM sensor_data ORDER BY created_at DESC LIMIT 1"
    )
    data = cursor.fetchone()

    cursor.close()
    db.close()

    return data

# ================================
# GET RIWAYAT SENSOR
# ================================
@app.get("/sensor/history")
def get_sensor_history(limit: int = 20):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM sensor_data ORDER BY created_at DESC LIMIT %s", (limit,)
    )
    data = cursor.fetchall()

    cursor.close()
    db.close()

    return data

# ================================
# SET STATUS POMPA
# ================================
@app.post("/pump")
def set_pump(status: str, mode: str):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("DELETE FROM pump_control")
    cursor.execute(
        "INSERT INTO pump_control (status, mode) VALUES (%s, %s)",
        (status, mode)
    )
    db.commit()

    cursor.close()
    db.close()

    return {"message": "Status pompa diperbarui"}

# ================================
# GET STATUS POMPA
# ================================
@app.get("/pump")
def get_pump_status():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM pump_control ORDER BY updated_at DESC LIMIT 1"
    )
    data = cursor.fetchone()

    cursor.close()
    db.close()

    return data
