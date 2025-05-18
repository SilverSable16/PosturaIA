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

# Modelo para la entrada del usuario
class MensajeUsuario(BaseModel):
    mensaje: str

# Ruta para procesar el mensaje del usuario
@app.post("/analizar")
def analizar_mensaje(data: MensajeUsuario):
    respuesta = procesar_prompt(data.mensaje)
    return {"respuesta": respuesta}
