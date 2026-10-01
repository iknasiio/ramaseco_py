from database import conectar
from database import (
    crear_trabajador,
    eliminar_trabajador,
    obtener_trabajadores,
)


def crear_solicitud(
    usuario_id,
    nombre,
    telefono,
    direccion,
    cantidad,
    foto,
    observacion,
    latitud,
    longitud,
    comuna,
    tipo_retiro,
):

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO solicitudes (
            usuario_id,
            nombre,
            telefono,
            direccion,
            cantidad,
            foto,
            observacion,
            latitud,
            longitud,
            comuna,
            tipo_retiro,
            estado
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        usuario_id,
        nombre,
        telefono,
        direccion,
        cantidad,
        foto,
        observacion,
        latitud,
        longitud,
        comuna,
        tipo_retiro,
        "Pendiente"
    ))

    conexion.commit()
    conexion.close()


def obtener_solicitudes():

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            id,
            nombre,
            telefono,
            direccion,
            cantidad,
            estado,
            fecha,
            trabajador_id,
            observacion_trabajador,
            comuna,
            tipo_retiro
        FROM solicitudes
        ORDER BY fecha ASC
    """)

    solicitudes = cursor.fetchall()

    conexion.close()

    return solicitudes


def obtener_solicitudes_usuario(usuario_id):

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            id,
            direccion,
            cantidad,
            estado,
            fecha,
            observacion_trabajador,
            comuna,
            tipo_retiro
        FROM solicitudes
        WHERE usuario_id = ?
        ORDER BY fecha DESC
    """, (usuario_id,))

    solicitudes = cursor.fetchall()

    conexion.close()

    return solicitudes


def aceptar_solicitud(solicitud_id, trabajador_id):

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE solicitudes
        SET
            estado = 'Aceptada',
            trabajador_id = ?
        WHERE id = ?
    """, (
        trabajador_id,
        solicitud_id
    ))

    conexion.commit()
    conexion.close()


def reasignar_solicitud(solicitud_id, trabajador_id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        UPDATE solicitudes
        SET trabajador_id = ?, estado = 'Aceptada'
        WHERE id = ?
    """, (trabajador_id, solicitud_id))
    conexion.commit()
    actualizado = cursor.rowcount > 0
    conexion.close()
    return actualizado


def eliminar_solicitud(solicitud_id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM solicitudes WHERE id = ?", (solicitud_id,))
    conexion.commit()
    eliminado = cursor.rowcount > 0
    conexion.close()
    return eliminado


def rechazar_solicitud(solicitud_id):

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE solicitudes
        SET estado = 'Rechazada'
        WHERE id = ?
    """, (solicitud_id,))

    conexion.commit()
    conexion.close()


def obtener_solicitudes_trabajador(trabajador_id):

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            id,
            nombre,
            telefono,
            direccion,
            cantidad,
            estado,
            latitud,
            longitud,
            observacion,
            comuna,
            tipo_retiro
        FROM solicitudes
        WHERE trabajador_id = ?
        ORDER BY fecha ASC
    """, (trabajador_id,))

    solicitudes = cursor.fetchall()

    conexion.close()

    return solicitudes


def actualizar_solicitud_trabajador(
    solicitud_id,
    estado,
    observacion
):

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE solicitudes
        SET
            estado = ?,
            observacion_trabajador = ?
        WHERE id = ?
    """, (
        estado,
        observacion,
        solicitud_id
    ))

    conexion.commit()
    conexion.close()