from fastapi import FastAPI
import mysql.connector
import os

app = FastAPI(title="Smart Farm Health Monitoring API")

# Koneksi Database (Railway Friendly)
db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)

cursor = db.cursor(dictionary=True)

# ================================
# POST DATA SENSOR (ESP32)
# ================================
@app.post("/sensor")
def insert_sensor(ph_value: float, soil_moisture: int):
    query = """
    INSERT INTO sensor_data (ph_value, soil_moisture)
    VALUES (%s, %s)
    """
    cursor.execute(query, (ph_value, soil_moisture))
    db.commit()
    return {"message": "Data sensor berhasil disimpan"}

# ================================
# GET DATA SENSOR TERAKHIR
# ================================
@app.get("/sensor/latest")
def get_latest_sensor():
    cursor.execute(
        "SELECT * FROM sensor_data ORDER BY created_at DESC LIMIT 1"
    )
    return cursor.fetchone()

# ================================
# GET RIWAYAT SENSOR
# ================================
@app.get("/sensor/history")
def get_sensor_history(limit: int = 20):
    cursor.execute(
        "SELECT * FROM sensor_data ORDER BY created_at DESC LIMIT %s", (limit,)
    )
    return cursor.fetchall()

# ================================
# SET STATUS POMPA
# ================================
@app.post("/pump")
def set_pump(status: str, mode: str):
    cursor.execute("DELETE FROM pump_control")
    cursor.execute(
        "INSERT INTO pump_control (status, mode) VALUES (%s, %s)",
        (status, mode)
    )
    db.commit()
    return {"message": "Status pompa diperbarui"}

# ================================
# GET STATUS POMPA (ESP32 BACA)
# ================================
@app.get("/pump")
def get_pump_status():
    cursor.execute(
        "SELECT * FROM pump_control ORDER BY updated_at DESC LIMIT 1"
    )
    return cursor.fetchone()
