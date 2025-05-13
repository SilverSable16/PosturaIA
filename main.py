from ia import procesar_prompt

def iniciar_conversacion():
    print("¡Hola! Soy el agente que te ayudará con la postura.")
    
    while True:
        mensaje_usuario = input("Tú: ").strip().lower()
        
        # Procesamos el mensaje con la lógica del agente
        respuesta = procesar_prompt(mensaje_usuario)
        
        print(f"Agente: {respuesta}")
        
        # Si el mensaje es de despedida, terminamos la conversación
        if "adios" in mensaje_usuario or "salir" in mensaje_usuario or "nos vemos" in mensaje_usuario or "chau" in mensaje_usuario:
            break

if __name__ == "__main__":
    iniciar_conversacion()
