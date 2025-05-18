from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ia import procesar_prompt

app = FastAPI()

# Configurar CORS para permitir peticiones desde tu frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # cámbialo a tu dominio de producción si es necesario
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class AnalisisEntrada(BaseModel):
    user_id: int
    score: float
    status: str
    posture_id: int

# Modelo para la entrada del usuario
class MensajeUsuario(BaseModel):
    mensaje: str

# Ruta para procesar el mensaje del usuario
@app.post("/analisis")
def registrar_analisis(data: AnalisisEntrada):
    db = conectar_db()
    cursor = db.cursor()
    try:
        query = """
        INSERT INTO posture_analyses (user_id, posture_score, status, posture_id, createdAt, updatedAt)
        VALUES (%s, %s, %s, %s, NOW(), NOW())
        """
        cursor.execute(query, (data.user_id, data.score, data.status, data.posture_id))
        db.commit()
        return {"message": "Análisis guardado con éxito"}
    finally:
        cursor.close()
        db.close()

@app.get("/posturas")
def obtener_posturas():
    db = conectar_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, name, body_part, description FROM postures")
        posturas = cursor.fetchall()
        return JSONResponse(content=posturas)
    finally:
        cursor.close()
        db.close()

