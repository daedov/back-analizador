from sqlalchemy import create_engine

# Cambia las credenciales según tu configuración
engine = create_engine("mysql+pymysql://admin:admin24@localhost/transcriptions_db")
try:
    connection = engine.connect()
    print("Conexión a la base de datos exitosa")
    connection.close()
except Exception as e:
    print(f"Error al conectar a la base de datos: {e}")
