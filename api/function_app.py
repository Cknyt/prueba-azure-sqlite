import azure.functions as func
import json
import os
import pymssql

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="socios")
def obtener_socios(req: func.HttpRequest) -> func.HttpResponse:
    # 1. Leer parámetros o cadena de conexión
    conn_str = os.environ.get("SQL_CONNECTION_STRING", "")

    # Parsear los parámetros de la cadena de conexión
    params = {}
    for part in conn_str.split(";"):
        if "=" in part:
            k, v = part.split("=", 1)
            params[k.strip().lower()] = v.strip().strip("{}")

    # Extraer servidor (limpiando prefijo tcp: y puerto)
    server = params.get("server", "").replace("tcp:", "").split(",")[0]
    user = params.get("uid", "") or params.get("user id", "")
    password = params.get("pwd", "") or params.get("password", "")
    database = params.get("database", "") or params.get("initial catalog", "")

    if not server or not password:
        return func.HttpResponse(
            body=json.dumps({"error": "Configuración de conexión incompleta en las variables de entorno"}),
            mimetype="application/json",
            status_code=500
        )

    try:
        # 2. Conectar directamente a Azure SQL Database sin depender de drivers ODBC
        conn = pymssql.connect(
            server=server,
            user=user,
            password=password,
            database=database,
            as_dict=True
        )
        cursor = conn.cursor()

        # 3. Consultar la tabla real
        cursor.execute("SELECT Id, Nombre, Email, AportacionMensual FROM Socios")
        filas = cursor.fetchall()
        conn.close()

        # 4. Formatear los resultados para la web
        resultado = [
            {
                "id": fila["Id"],
                "nombre": fila["Nombre"],
                "rol": fila["Email"],
                "aportacion": float(fila["AportacionMensual"])
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
