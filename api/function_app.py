import azure.functions as func
import json
import sqlite3

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="socios")
def obtener_socios(req: func.HttpRequest) -> func.HttpResponse:
    # 1. Conexión a SQLite (en memoria para el laboratorio)
    conexion = sqlite3.connect(":memory:")
    cursor = conexion.cursor()

    # 2. Ejecutar sentencias SQL reales: Crear tabla e insertar registros de prueba
    cursor.execute("""
        CREATE TABLE socios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            rol TEXT NOT NULL,
            aportacion INTEGER NOT NULL
        )
    """)
    
    socios_iniciales = [
        ("María García", "Coordinadora", 50),
        ("Carlos López", "Voluntario", 20),
        ("Asociación Amiga", "Socio Protector", 150)
    ]
    cursor.executemany("INSERT INTO socios (nombre, rol, aportacion) VALUES (?, ?, ?)", socios_iniciales)
    conexion.commit()

    # 3. Consulta SQL SELECT
    cursor.execute("SELECT id, nombre, rol, aportacion FROM socios")
    filas = cursor.fetchall()
    conexion.close()

    # 4. Formatear como lista de objetos JSON
    resultado = [
        {"id": fila[0], "nombre": fila[1], "rol": fila[2], "aportacion": fila[3]}
        for fila in filas
    ]

    return func.HttpResponse(
        body=json.dumps(resultado, ensure_ascii=False),
        mimetype="application/json",
        status_code=200
    )
