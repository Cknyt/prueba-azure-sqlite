import azure.functions as func
import json
import os
import pymssql

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="socios")
def obtener_socios(req: func.HttpRequest) -> func.HttpResponse:
    # 1. Leer las variables limpias del entorno
    server = os.environ.get("DB_SERVER")
    database = os.environ.get("DB_NAME")
    user = os.environ.get("DB_USER")
    password = os.environ.get("DB_PASSWORD")

    if not all([server, database, user, password]):
        return func.HttpResponse(
            body=json.dumps({"error": "Faltan variables: revisa DB_SERVER, DB_NAME, DB_USER, DB_PASSWORD"}),
            mimetype="application/json",
            status_code=500
        )

    try:
        # 2. Conexión directa
        conn = pymssql.connect(
            server=server,
            user=user,
            password=password,
            database=database,
            as_dict=True
        )
        cursor = conn.cursor()

        # 3. Consulta a la tabla real
        cursor.execute("SELECT Id, Nombre, Email, AportacionMensual FROM Socios")
        filas = cursor.fetchall()
        conn.close()

        # 4. Formatear resultados
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
