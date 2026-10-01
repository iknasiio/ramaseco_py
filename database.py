import sqlite3
from pathlib import Path

DATABASE = Path(__file__).resolve().parent / "temuco_retira.db"


def conectar():
    return sqlite3.connect(DATABASE)


def crear_tablas():
    conexion = conectar()
    cursor = conexion.cursor()

    # Tabla de usuarios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            correo TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            rol TEXT NOT NULL
        )
    """)

    # Tabla de solicitudes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS solicitudes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            telefono TEXT NOT NULL,
            direccion TEXT NOT NULL,
            cantidad TEXT NOT NULL,
            foto TEXT,
            observacion TEXT,
            latitud REAL,
            longitud REAL,
            estado TEXT NOT NULL DEFAULT 'Pendiente',
            trabajador_id INTEGER,
            observacion_trabajador TEXT,
            comuna TEXT NOT NULL DEFAULT 'Temuco',
            tipo_retiro TEXT NOT NULL DEFAULT 'Ramas',
            fecha DATETIME DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (usuario_id)
            REFERENCES usuarios(id),

            FOREIGN KEY (trabajador_id)
            REFERENCES usuarios(id)
        )
    """)

    columnas = {
        fila[1]
        for fila in cursor.execute("PRAGMA table_info(solicitudes)").fetchall()
    }
    if "comuna" not in columnas:
        cursor.execute(
            "ALTER TABLE solicitudes ADD COLUMN comuna TEXT NOT NULL DEFAULT 'Temuco'"
        )
    if "tipo_retiro" not in columnas:
        cursor.execute(
            "ALTER TABLE solicitudes ADD COLUMN tipo_retiro TEXT NOT NULL DEFAULT 'Ramas'"
        )

    conexion.commit()
    conexion.close()


def crear_usuarios_iniciales():

    conexion = conectar()
    cursor = conexion.cursor()

    # Administrador
    cursor.execute("""
        INSERT OR IGNORE INTO usuarios
        (nombre, correo, password, rol)
        VALUES (?, ?, ?, ?)
    """, (
        "Administrador Municipal",
        "admin@temucoretira.cl",
        "admin123",
        "administrador"
    ))

    # Trabajador
    cursor.execute("""
        INSERT OR IGNORE INTO usuarios
        (nombre, correo, password, rol)
        VALUES (?, ?, ?, ?)
    """, (
        "Trabajador Municipal",
        "trabajador@temucoretira.cl",
        "trabajador123",
        "trabajador"
    ))

    cursor.execute("""
        INSERT OR IGNORE INTO usuarios
        (nombre, correo, password, rol)
        VALUES (?, ?, ?, ?)
    """, (
        "Ciudadano de Prueba",
        "ciudadano@temucoretira.cl",
        "ciudadano123",
        "ciudadano"
    ))

    trabajadores_demo = (
        (
            "Trabajadora Municipal 2",
            "trabajadora2@temucoretira.cl",
            "trabajadora123"
        ),
        (
            "Trabajador Municipal 3",
            "trabajador3@temucoretira.cl",
            "trabajador321"
        )
    )

    for nombre, correo, password in trabajadores_demo:
        cursor.execute("""
            INSERT OR IGNORE INTO usuarios
            (nombre, correo, password, rol)
            VALUES (?, ?, ?, 'trabajador')
        """, (nombre, correo, password))

    conexion.commit()
    conexion.close()


def buscar_usuario(correo, password):

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT id, nombre, correo, rol
        FROM usuarios
        WHERE correo = ? AND password = ?
    """, (correo, password))

    usuario = cursor.fetchone()

    conexion.close()

    return usuario


def obtener_trabajadores():

    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT id, nombre, correo
        FROM usuarios
        WHERE rol = 'trabajador'
        ORDER BY nombre
    """)
    trabajadores = cursor.fetchall()
    conexion.close()
    return trabajadores


def crear_trabajador(nombre, correo, password):

    conexion = conectar()
    cursor = conexion.cursor()

    try:
        cursor.execute("""
            INSERT INTO usuarios (nombre, correo, password, rol)
            VALUES (?, ?, ?, 'trabajador')
        """, (nombre, correo, password))
        conexion.commit()
    except sqlite3.IntegrityError as error:
        conexion.rollback()
        if "UNIQUE" in str(error).upper():
            raise ValueError("Ese correo ya está registrado.") from error
        raise ValueError("No se pudo registrar el trabajador.") from error
    finally:
        conexion.close()


def eliminar_trabajador(trabajador_id):

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM solicitudes
        WHERE trabajador_id = ?
    """, (trabajador_id,))

    if cursor.fetchone()[0]:
        conexion.close()
        raise ValueError(
            "No se puede eliminar: tiene solicitudes asignadas."
        )

    cursor.execute("""
        DELETE FROM usuarios
        WHERE id = ? AND rol = 'trabajador'
    """, (trabajador_id,))
    conexion.commit()
    eliminado = cursor.rowcount > 0
    conexion.close()

    if not eliminado:
        raise ValueError("El trabajador no existe.")