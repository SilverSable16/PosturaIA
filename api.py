from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ia import procesar_prompt
from db import conectar_db
from fastapi.responses import JSONResponse
import psycopg2.extras

app = FastAPI()

# Configurar CORS para permitir peticiones desde tu frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Asegura que esto esté activo
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
    try:
        db = conectar_db()
        cursor = db.cursor()
        query = """
        INSERT INTO posture_analyses ("user_id", "posture_score", "status", "posture_id", "createdAt", "updatedAt")
        VALUES (%s, %s, %s, %s, NOW(), NOW())
        """
        cursor.execute(query, (data.user_id, data.score, data.status, data.posture_id))
        db.commit()
        return {"message": "Análisis guardado con éxito"}
    except Exception as e:
        print("❌ Error al registrar análisis:", e)
        return JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        cursor.close()
        db.close()


@app.get("/posturas")
def obtener_posturas():
    db = conectar_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cursor.execute("SELECT id, name, body_part, description FROM postures")
        posturas = cursor.fetchall()
        # Convertir los resultados a lista de diccionarios
        posturas_dict = [dict(row) for row in posturas]
        return JSONResponse(content=posturas_dict)
    finally:
        cursor.close()
        db.close()

@app.post("/ia")
def procesar_ia(data: MensajeUsuario):
    respuesta = procesar_prompt(data.mensaje)
    return {"respuesta": respuesta}

