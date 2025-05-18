from db import conectar_db
import re
from datetime import datetime, timedelta
from fpdf import FPDF
import tkinter as tk
from tkinter import filedialog

# Variable para la postura actual
postura_actual = None

def guardar_conversacion(mensaje_usuario, respuesta_agente):
    db = conectar_db()
    cursor = db.cursor()
    
    query_check = "SELECT COUNT(*) FROM Conversaciones WHERE mensaje_usuario = %s AND respuesta_agente = %s"
    cursor.execute(query_check, (mensaje_usuario, respuesta_agente))
    count = cursor.fetchone()[0]
    

    if count == 0:
        query = "INSERT INTO Conversaciones (mensaje_usuario, respuesta_agente) VALUES (%s, %s)"
        cursor.execute(query, (mensaje_usuario, respuesta_agente))
        db.commit()  # Aseguramos que la transacción se guarde en la base de datos
    
    cursor.close()
    db.close()

def obtener_respuesta(tipo, mensaje_usuario):
    db = conectar_db()
    cursor = db.cursor(dictionary=True)
    

    query = "SELECT respuesta_agente FROM RespuestasSaludo WHERE tipo = %s AND mensaje_usuario = %s"
    cursor.execute(query, (tipo, mensaje_usuario))
    
    resultado = cursor.fetchone()
    cursor.close()
    db.close()
    
    if resultado:
        return resultado['respuesta_agente']
    else:
        return "Lo siento, no entiendo esa frase. ¿Puedes intentar de nuevo?"
    

def obtener_respuestas_comunes(tiempo_periodo):
    db = conectar_db()
    cursor = db.cursor(dictionary=True)


    if tiempo_periodo == "hoy":
        fecha_inicio = datetime.now().strftime('%Y-%m-%d') 
        query = """
            SELECT respuesta_agente, COUNT(*) AS conteo
            FROM conversaciones
            WHERE DATE(fecha) = %s
            GROUP BY respuesta_agente
            ORDER BY conteo DESC
            LIMIT 5
        """
        cursor.execute(query, (fecha_inicio,))
    elif tiempo_periodo == "semana":
        fecha_inicio = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        query = """
            SELECT respuesta_agente, COUNT(*) AS conteo
            FROM conversaciones
            WHERE DATE(fecha) >= %s
            GROUP BY respuesta_agente
            ORDER BY conteo DESC
            LIMIT 5
        """
        cursor.execute(query, (fecha_inicio,))
    elif tiempo_periodo == "mes":
        fecha_inicio = datetime.now().replace(day=1).strftime('%Y-%m-%d')
        query = """
            SELECT respuesta_agente, COUNT(*) AS conteo
            FROM conversaciones
            WHERE DATE(fecha) >= %s
            GROUP BY respuesta_agente
            ORDER BY conteo DESC
            LIMIT 5
        """
        cursor.execute(query, (fecha_inicio,))
    else:
        return "Período de tiempo no reconocido. Usa 'hoy', 'semana' o 'mes'."

    resultados = cursor.fetchall()
    cursor.close()
    db.close()

    # Si se obtienen resultados, los mostramos de manera más fluida
    if resultados:
        respuestas_texto = f"Las respuestas más comunes de este {tiempo_periodo} son:\n"
        for i, resultado in enumerate(resultados, 1):
            respuestas_texto += f"{i}. {resultado['respuesta_agente']} (Repetida {resultado['conteo']} veces)\n"
        return respuestas_texto
    else:
        return f"No se encontraron respuestas comunes en el {tiempo_periodo} solicitado."





def obtener_recomendacion(postura_nombre):
    db = conectar_db()
    cursor = db.cursor(dictionary=True)
    
    query = "SELECT * FROM Posturas WHERE nombre LIKE %s"
    cursor.execute(query, (f"%{postura_nombre}%",))
    
    resultado = cursor.fetchone()
    if resultado:
        # Formateamos la respuesta de manera más natural
        return f"¡Claro! Para la postura {resultado['nombre']}, que se caracteriza por {resultado['descripcion'].lower()}, te recomendamos lo siguiente: {resultado['recomendacion'].lower()}. \n¿Te puedo ayudar con algo más?"
    else:
        return "Lo siento, no encontré información sobre esa postura. ¿Puedes intentar de nuevo?"
    
    cursor.close()
    db.close()

def obtener_ejercicios(postura_nombre):
    db = conectar_db()
    cursor = db.cursor(dictionary=True)
    
    query = """
        SELECT ejercicios.ejercicio, ejercicios.descripcion AS ejercicio_descripcion 
        FROM ejercicios 
        JOIN posturas ON posturas.id = ejercicios.postura_id
        WHERE posturas.nombre LIKE %s
    """
    cursor.execute(query, (f"%{postura_nombre}%",))
    
    resultados = cursor.fetchall()
    if resultados:
        ejercicios_texto = ""
        for ejercicio in resultados:
            ejercicios_texto += f"- {ejercicio['ejercicio']}: {ejercicio['ejercicio_descripcion']}\n"
        return f"¡Por supuesto! Para mejorar la postura de {postura_nombre}, te recomiendo los siguientes ejercicios:\n{ejercicios_texto}¿Te gustaría que te ayudara con algo más?"
    else:
        return "No pude encontrar ejercicios específicos para esa postura. ¿Te gustaría intentar con otra postura?"
    
    cursor.close()
    db.close()

def obtener_listado_posturas():
    db = conectar_db()
    cursor = db.cursor(dictionary=True)
    
    query = "SELECT nombre FROM Posturas"
    cursor.execute(query)
    
    resultados = cursor.fetchall()
    cursor.close()
    db.close()

    if resultados:
        listado_texto = "Aquí tienes el listado de posturas disponibles:\n"
        for i, resultado in enumerate(resultados, 1):
            listado_texto += f"{i}. {resultado['nombre']}\n"
        return listado_texto
    else:
        return "No se encontraron posturas en la base de datos."

def obtener_listado_ejercicios():
    db = conectar_db()
    cursor = db.cursor(dictionary=True)
    
    query = "SELECT ejercicio FROM Ejercicios"
    cursor.execute(query)
    
    resultados = cursor.fetchall()
    cursor.close()
    db.close()

    if resultados:
        listado_texto = "Aquí tienes el listado de ejercicios disponibles:\n"
        for i, resultado in enumerate(resultados, 1):
            listado_texto += f"{i}. {resultado['ejercicio']}\n"
        return listado_texto
    else:
        return "No se encontraron ejercicios en la base de datos."



postura_actual = None

def crear_pdf_respuesta(postura, recomendacion, ejercicios):

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    

    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Consulta de Postura", ln=True, align="C")
    
    pdf.ln(10)
    fecha_hoy = datetime.now().strftime('%d/%m/%Y')
    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 10, txt=f"Fecha: {fecha_hoy}", ln=True)
    

    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt=f"Postura: {postura}", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 10, txt=recomendacion)  # Descripción de la recomendación
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Ejercicios recomendados:", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 10, txt=ejercicios) 
    
   
    root = tk.Tk()
    root.withdraw() 
    
    file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if file_path:
        pdf.output(file_path)  # Guardar el archivo PDF
        return f"El PDF se ha guardado en: {file_path}"
    else:
        return "No se seleccionó ninguna ubicación para guardar el archivo."



def procesar_prompt(prompt):
    global postura_actual
    
    prompt = prompt.strip().lower()

    saludos = ["hola", "como estas", "que hay", "oye", "buenos dias", "buenas tardes", "buenas noches"]
    despedidas = ["adios", "salir", "nos vemos", "chau"]
    

    if prompt in saludos:
        respuesta = obtener_respuesta('saludo', prompt)
        guardar_conversacion(prompt, respuesta) 
        return respuesta
    

    elif prompt in despedidas:
        respuesta = obtener_respuesta('despedida', prompt)
        guardar_conversacion(prompt, respuesta) 
        return respuesta
    
 
    if "respuestas" in prompt and ("comunes" in prompt or "comunes del mes" in prompt or "comunes de la semana" in prompt or "comunes hoy" in prompt):
        if "hoy" in prompt:
            respuesta = obtener_respuestas_comunes("hoy")
        elif "semana" in prompt:
            respuesta = obtener_respuestas_comunes("semana")
        elif "mes" in prompt:
            respuesta = obtener_respuestas_comunes("mes")
        else:
            respuesta = "Por favor, dime si quieres las respuestas comunes de hoy, semana o mes."
        
        guardar_conversacion(prompt, respuesta)  
        return respuesta
    

    if "listado de las posturas" in prompt:
        respuesta = obtener_listado_posturas()
        guardar_conversacion(prompt, respuesta) 
        return respuesta
    
    if "listado de los ejercicios" in prompt:
        respuesta = obtener_listado_ejercicios()
        guardar_conversacion(prompt, respuesta)  
        return respuesta
    
    match = re.search(r"(postura|ejercicios\s+para\s+la\s+postura)\s+(\w+(\s\w+)*)", prompt)
    if match:
        postura = match.group(2).strip()  
        postura_actual = postura  
        

        if "postura" in match.group(1):
            respuesta = obtener_recomendacion(postura)
   
        elif "ejercicios" in match.group(1):
            respuesta = obtener_ejercicios(postura)
        
        guardar_conversacion(prompt, respuesta) 
        return respuesta
    

    if "ejercicios" in prompt:
        if postura_actual:
            respuesta = obtener_ejercicios(postura_actual)
            guardar_conversacion(prompt, respuesta) 
            return respuesta
        else:
            respuesta = "¿Puedes decirme de qué postura quieres los ejercicios? Por ejemplo, 'ejercicios para postura encorvado'."
            guardar_conversacion(prompt, respuesta)  
            return respuesta
    
    if "crea un pdf" in prompt or "guardar como pdf" in prompt:
        respuesta = crear_pdf_respuesta(postura_actual, "Recomendación para la postura", "Ejercicios recomendados para la postura.")
        guardar_conversacion(prompt, respuesta)  
        return respuesta
    
    else:
        respuesta = "Lo siento, no entendí eso. ¿Puedes intentar de nuevo?"
        guardar_conversacion(prompt, respuesta) 
        return respuesta
