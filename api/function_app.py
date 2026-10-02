import azure.functions as func
import json
import os
import pyodbc

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="socios")
def obtener_socios(req: func.HttpRequest) -> func.HttpResponse:
    # 1. Leer la cadena secreta de las variables de entorno de Azure
    connection_string = os.environ.get("SQL_CONNECTION_STRING")
    
    if not connection_string:
        return func.HttpResponse(
            body=json.dumps({"error": "No se encontró la variable SQL_CONNECTION_STRING"}),
            mimetype="application/json",
            status_code=500
        )

    try:
        # 2. Conectar a Azure SQL Database
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        # 3. Consultar la tabla Socios creada en el Query Editor
        cursor.execute("SELECT Id, Nombre, Email, AportacionMensual FROM Socios")
        filas = cursor.fetchall()
        conn.close()

        # 4. Formatear a JSON
        resultado = [
            {
                "id": fila[0],
                "nombre": fila[1],
                "rol": fila[2],  # mostramos el email en la columna de rol/contacto
                "aportacion": float(fila[3])
            }
            for fila in filas
        ]

        return func.HttpResponse(
            body=json.dumps(resultado, ensure_ascii=False),
            mimetype="application/json",
            status_code=200
        )

    except Exception as e:
        return func.HttpResponse(
            body=json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )
