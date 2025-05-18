import psycopg2

def conectar_db():
    try:
        conexion = psycopg2.connect(
            dbname="pp_ai_sgav",
            user="postura1",
            password="1JHQPUSyIXkhncpNqoIutf1yLRZd6AQ7",
            host="dpg-d0kgg1ogjchc73adakag-a.oregon-postgres.render.com",
            port="5432"
        )
        return conexion
    except Exception as e:
        print("Error al conectar a la base de datos:", e)
        return None
