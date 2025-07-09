import sqlite3
import hashlib
import http.server
import socketserver
import os
from tabulate import tabulate # ¡ASEGÚRATE DE QUE ESTA LÍNEA ESTÉ AQUÍ!

DATABASE_NAME = 'users.db'
PORT = 5800
USERS = {
    "Jorge Villaseca": "cisco1",
    "Bastian Fernandez": "cisco2",
    "Diego Riquelme": "cisco3"
}

def create_database():
    """Crea la base de datos y la tabla de usuarios si no existen."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    print(f"Base de datos '{DATABASE_NAME}' creada o ya existente.")

def hash_password(password):
    """Hashea una contraseña usando SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

def add_user(username, password):
    """Agrega un usuario a la base de datos con la contraseña hasheada."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    password_hash = hash_password(password)
    try:
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
        conn.commit()
        print(f"Usuario '{username}' agregado exitosamente.")
    except sqlite3.IntegrityError:
        print(f"El usuario '{username}' ya existe en la base de datos. Actualizando contraseña si es diferente.")
        # Opcional: Si el usuario ya existe, podrías actualizar la contraseña
        cursor.execute("UPDATE users SET password_hash = ? WHERE username = ?", (password_hash, username))
        conn.commit()
        print(f"Contraseña de '{username}' actualizada.")
    finally:
        conn.close()

def validate_user(username, password):
    """Valida un usuario comparando el hash de la contraseña ingresada con el almacenado."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()

    if result:
        stored_password_hash = result[0]
        if stored_password_hash == hash_password(password):
            return True
    return False

def show_users_in_db():
    """Muestra los usuarios y sus hashes de contraseña desde la base de datos."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT username, password_hash FROM users")
    users = cursor.fetchall()
    conn.close()

    if users:
        print("\n--- Usuarios en la Base de Datos (para demostración con DB Browser) ---")
        headers = ["Usuario", "Hash de Contraseña (SHA256)"]
        table_data = [[u[0], u[1]] for u in users]
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
    else:
        print("No hay usuarios en la base de datos.")

def run_web_server():
    """Inicia un servidor web básico en el puerto especificado."""
    # Crea un archivo index.html simple para que el servidor lo sirva
    with open("index.html", "w") as f:
        f.write("<!DOCTYPE html>\n<html>\n<head><title>Bienvenido</title></head>\n<body>\n")
        f.write("<h1>Servidor Web del Examen Transversal - DRY7122</h1>\n")
        f.write("<p>Este es el sitio web del Item 3, corriendo en el puerto 5800.</p>\n")
        f.write("<p>Usuarios registrados:</p><ul>")
        for user in USERS:
            f.write(f"<li>{user}</li>")
        f.write("</ul></body>\n</html>")

    Handler = http.server.SimpleHTTPRequestHandler

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"\nServidor web corriendo en http://localhost:{PORT}")
        print("Para detener el servidor, presione Ctrl+C en esta terminal.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor web detenido.")
        finally:
            # Limpiar el archivo index.html creado
            if os.path.exists("index.html"):
                os.remove("index.html")
                print("Archivo index.html temporal eliminado.")


def main():
    create_database()

    # Añadir los usuarios y sus contraseñas hasheadas a la base de datos
    print("\n--- Agregando usuarios a la base de datos ---")
    for username, password in USERS.items():
        add_user(username, password)

    show_users_in_db() # Mostrar usuarios para la demostración con DB Browser

    # Parte de validación de usuarios
    print("\n--- Validación de Usuarios ---")
    while True:
        input_username = input("Ingrese nombre de usuario para validar (o 's' para salir): ")
        if input_username.lower() == 's':
            break
        input_password = input("Ingrese contraseña: ")

        if validate_user(input_username, input_password):
            print(f"¡Usuario '{input_username}' validado exitosamente!")
        else:
            print(f"Error de validación para '{input_username}'. Usuario o contraseña incorrectos.")

    # Ejecutar el servidor web
    print("\n--- Iniciando Servidor Web ---")
    run_web_server()

if __name__ == "__main__":
    main()
