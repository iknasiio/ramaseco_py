from kivy.config import Config

Config.set("input", "mouse", "mouse,disable_multitouch")

from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivy.uix.spinner import Spinner

from database import buscar_usuario, crear_tablas, crear_usuarios_iniciales
from modelos import (
    aceptar_solicitud,
    actualizar_solicitud_trabajador,
    crear_solicitud,
    eliminar_solicitud,
    eliminar_trabajador,
    obtener_solicitudes,
    obtener_solicitudes_trabajador,
    obtener_solicitudes_usuario,
    reasignar_solicitud,
)
from database import crear_trabajador, obtener_trabajadores

Window.size = (400, 760)
Window.clearcolor = (0.96, 0.98, 0.94, 1)

VERDE = (0.08, 0.36, 0.25, 1)
VERDE_CLARO = (0.16, 0.55, 0.36, 1)
NARANJA = (0.90, 0.48, 0.15, 1)
ROJO = (0.70, 0.18, 0.16, 1)
BLANCO = (1, 1, 1, 1)
CREMA = (0.96, 0.98, 0.94, 1)
COMUNAS = ("Temuco", "Padre Las Casas", "Labranza")
TIPOS_RETIRO = ("Ramas", "Pasto", "Hojas", "Ramas y hojas", "Otro")


def campo(placeholder, password=False):
    entrada = MDTextField(
        hint_text=placeholder,
        password=password,
        multiline=False,
        size_hint_y=None,
        height=dp(48),
        font_size=dp(15),
        mode="rectangle",
        line_color_normal=(0.40, 0.47, 0.42, 1),
        line_color_focus=VERDE,
        text_color_normal=(0.12, 0.18, 0.14, 1),
        hint_text_color=(0.40, 0.47, 0.42, 1),
    )
    return entrada


def boton(texto, color=VERDE_CLARO):
    button = MDRaisedButton(
        text=texto,
        size_hint_y=None,
        height=dp(50),
        font_size=dp(15),
        theme_text_color="Custom",
        text_color=BLANCO,
        md_bg_color=color,
        elevation=2,
    )
    button.size_hint_x = 0.94
    button.pos_hint = {"center_x": 0.5}
    return button


def selector(texto):
    return Spinner(
        text=texto,
        values=(),
        size_hint_x=0.96,
        size_hint_y=None,
        height=dp(50),
        font_size=dp(14),
        padding=(dp(12), 0),
        pos_hint={"center_x": 0.5},
        color=(0.10, 0.18, 0.13, 1),
        background_normal="",
        background_down="",
        background_color=(0, 0, 0, 0),
    )


def panel(contenido, alto):
    tarjeta = MDCard(
        orientation="vertical",
        padding=dp(14),
        spacing=dp(10),
        size_hint_x=0.94,
        size_hint_y=None,
        height=dp(alto),
        pos_hint={"center_x": 0.5},
        radius=[dp(16), dp(16), dp(16), dp(16)],
        elevation=3,
        shadow_softness=8,
        line_color=(0.72, 0.82, 0.74, 1),
        line_width=dp(1),
        md_bg_color=BLANCO,
    )
    tarjeta.add_widget(contenido)
    return tarjeta


def popup_estilizado(titulo, contenido, ancho=0.9, alto=0.7):
    return Popup(
        title=titulo,
        content=contenido,
        size_hint=(ancho, alto),
        separator_color=VERDE,
        background_color=(0.98, 1, 0.98, 1),
        title_color=VERDE,
    )


class BaseScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*CREMA)
            self.fondo = Rectangle(pos=self.pos, size=self.size)
            Color(*VERDE)
            self.banda = Rectangle(pos=self.pos, size=(self.width, dp(7)))
            Color(*NARANJA)
            self.acento = Rectangle(pos=(self.x, self.y), size=(dp(7), self.height))
        self.bind(pos=self.actualizar_fondo, size=self.actualizar_fondo)

    def actualizar_fondo(self, *_):
        self.fondo.pos = self.pos
        self.fondo.size = self.size
        self.banda.pos = (self.x, self.top - dp(7))
        self.banda.size = (self.width, dp(7))
        self.acento.pos = self.pos
        self.acento.size = (dp(7), self.height)

    def contenido(self, titulo):
        layout = BoxLayout(
            orientation="vertical",
            padding=(dp(20), dp(10), dp(20), dp(24)),
            spacing=dp(10),
        )
        layout.add_widget(Image(
            source="assets/hoja-temuco.png",
            fit_mode="contain",
            size_hint_y=None,
            height=dp(75),
        ))
        layout.add_widget(MDLabel(
            text="TEMUCO RETIRA",
            color=VERDE,
            font_size=dp(21),
            bold=True,
            halign="center",
            size_hint_y=None,
            height=dp(34),
        ))
        layout.add_widget(MDLabel(
            text=titulo,
            color=(0.10, 0.18, 0.13, 1),
            font_size=dp(25),
            bold=True,
            halign="center",
            size_hint_y=None,
            height=dp(54),
        ))
        return layout

    def desplazar(self, layout):
        layout.size_hint_y = None
        layout.bind(minimum_height=layout.setter("height"))
        scroll = ScrollView(
            do_scroll_x=False,
            bar_width=dp(4),
            scroll_type=["bars", "content"],
        )
        scroll.add_widget(layout)
        return scroll

    def aviso(self, titulo, mensaje):
        contenido = BoxLayout(
            orientation="vertical",
            padding=dp(18),
            spacing=dp(14),
        )
        contenido.add_widget(MDLabel(
            text=mensaje,
            color=(0.08, 0.14, 0.10, 1),
            halign="center",
            valign="middle",
            text_size=(dp(285), None),
        ))
        cerrar = boton("ENTENDIDO", VERDE)
        contenido.add_widget(cerrar)
        popup = popup_estilizado(titulo, contenido, 0.88, 0.34)
        cerrar.bind(on_release=popup.dismiss)
        popup.open()


class LoginScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=(dp(22), dp(18)), spacing=dp(11))
        layout.add_widget(Image(
            source="assets/hoja-temuco.png",
            fit_mode="contain",
            size_hint_y=None,
            height=dp(155),
        ))
        layout.add_widget(MDLabel(
            text="TEMUCO RETIRA",
            color=VERDE,
            font_size=dp(34),
            bold=True,
            halign="center",
            size_hint_y=None,
            height=dp(56),
        ))
        layout.add_widget(MDLabel(
            text="Retiramos tus ramas, cuidamos Temuco",
            color=(0.25, 0.35, 0.28, 1),
            font_size=dp(14),
            halign="center",
            size_hint_y=None,
            height=dp(30),
        ))
        layout.add_widget(Widget(size_hint_y=None, height=dp(40)))
        self.correo = campo("Correo")
        self.password = campo("Contraseña", password=True)
        acceso = BoxLayout(orientation="vertical", spacing=dp(8))
        acceso.add_widget(self.correo)
        acceso.add_widget(self.password)
        layout.add_widget(panel(acceso, 138))
        ingresar = boton("INGRESAR", VERDE)
        ingresar.bind(on_release=self.iniciar_sesion)
        layout.add_widget(ingresar)
        layout.add_widget(MDLabel(
            text="Contacto de prueba: +56 9 9999 9999  Email: contacto@temuco.cl",
            color=(0.25, 0.35, 0.28, 1),
            font_size=dp(12),
            halign="center",
            size_hint_y=None,
            height=dp(30),
        ))
        self.add_widget(self.desplazar(layout))

    def iniciar_sesion(self, *_):
        if not self.correo.text.strip() or not self.password.text.strip():
            self.aviso("Datos faltantes", "Completa correo y contraseña.")
            return
        usuario = buscar_usuario(self.correo.text.strip(), self.password.text.strip())
        if not usuario:
            self.aviso("Error", "Correo o contraseña incorrectos.")
            return
        app = MDApp.get_running_app()
        app.usuario = usuario
        destino = {"administrador": "admin", "trabajador": "trabajador", "ciudadano": "ciudadano"}[usuario[3]]
        app.cargar_pantalla(destino)


class CiudadanoScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = self.contenido("Nueva solicitud")
        self.telefono = campo("Teléfono")
        self.direccion = campo("Dirección")
        self.comuna = selector("Selecciona la comuna")
        self.comuna.values = COMUNAS
        self.tipo_retiro = selector("Selecciona el tipo de retiro")
        self.tipo_retiro.values = TIPOS_RETIRO
        self.cantidad = campo("Cantidad: Poca, Media o Mucha")
        self.observacion = campo("Observación")
        formulario = BoxLayout(orientation="vertical", spacing=dp(10))
        for widget in (
            self.comuna,
            self.tipo_retiro,
            self.telefono,
            self.direccion,
            self.cantidad,
            self.observacion,
        ):
            formulario.add_widget(widget)
        self.layout.add_widget(panel(formulario, 380))
        enviar = boton("ENVIAR SOLICITUD", VERDE)
        enviar.bind(on_release=self.enviar)
        historial = boton("VER MIS SOLICITUDES", VERDE_CLARO)
        historial.bind(on_release=self.historial)
        salir = boton("CERRAR SESIÓN", ROJO)
        salir.bind(on_release=lambda *_: MDApp.get_running_app().cerrar_sesion())
        for button in (enviar, historial, salir):
            self.layout.add_widget(button)
        self.add_widget(self.desplazar(self.layout))

    def enviar(self, *_):
        campos = (
            (self.telefono.text.strip(), "teléfono"),
            (self.direccion.text.strip(), "dirección"),
            (self.cantidad.text.strip(), "cantidad"),
            (self.observacion.text.strip(), "observación"),
        )
        for valor, nombre in campos:
            if not valor:
                self.aviso("Campo incompleto", f"Completa el campo {nombre}.")
                return
        if self.comuna.text.startswith("Selecciona") or self.tipo_retiro.text.startswith("Selecciona"):
            self.aviso("Campo incompleto", "Selecciona comuna y tipo de retiro.")
            return
        usuario = MDApp.get_running_app().usuario
        crear_solicitud(
            usuario[0],
            usuario[1],
            self.telefono.text.strip(),
            self.direccion.text.strip(),
            self.cantidad.text.strip() or "Poca",
            "",
            self.observacion.text.strip(),
            None,
            None,
            self.comuna.text,
            self.tipo_retiro.text,
        )
        self.aviso("Solicitud enviada", "La solicitud fue registrada correctamente.")
        self.telefono.text = self.direccion.text = self.cantidad.text = self.observacion.text = ""
        self.comuna.text = "Selecciona la comuna"
        self.tipo_retiro.text = "Selecciona el tipo de retiro"

    def historial(self, *_):
        usuario = MDApp.get_running_app().usuario
        solicitudes = obtener_solicitudes_usuario(usuario[0])
        texto = "\n\n".join(
            f"Solicitud #{item[0]} | {item[6]} | {item[7]} | {item[1]}"
            for item in solicitudes
        ) or "No hay solicitudes registradas."
        self.aviso("Mis solicitudes", texto)


class AdminScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = self.contenido("Panel administrador")
        self.solicitudes = []
        self.comuna_filtro = selector("Todas las comunas")
        self.comuna_filtro.values = ("Todas las comunas",) + COMUNAS
        self.comuna_filtro.bind(text=lambda *_: self.mostrar_solicitudes())
        self.lista = selector("Selecciona una solicitud")
        self.trabajadores = selector("Selecciona un trabajador")
        filtros = BoxLayout(orientation="vertical", spacing=dp(10))
        filtros.add_widget(self.comuna_filtro)
        filtros.add_widget(self.lista)
        filtros.add_widget(self.trabajadores)
        self.layout.add_widget(panel(filtros, 175))
        acciones = (
            ("ACTUALIZAR SOLICITUDES", VERDE_CLARO, self.actualizar),
            ("ACEPTAR Y ASIGNAR", VERDE, self.aceptar),
            ("CAMBIAR TRABAJADOR", NARANJA, self.reasignar),
            ("ELIMINAR SOLICITUD", ROJO, self.eliminar),
            ("GESTIONAR TRABAJADORES", NARANJA, self.gestionar_trabajadores),
            ("CERRAR SESIÓN", ROJO, lambda *_: MDApp.get_running_app().cerrar_sesion()),
        )
        for texto, color, accion in acciones:
            accion_boton = boton(texto, color)
            accion_boton.bind(on_release=accion)
            self.layout.add_widget(accion_boton)
        self.add_widget(self.desplazar(self.layout))

    def actualizar(self, *_):
        self.solicitudes = obtener_solicitudes()
        self.mostrar_solicitudes()
        trabajadores = obtener_trabajadores()
        self.trabajadores.values = tuple(f"{item[0]} | {item[1]}" for item in trabajadores)
        if not trabajadores:
            self.trabajadores.text = "No hay trabajadores"

    def mostrar_solicitudes(self):
        solicitudes = self.solicitudes
        if self.comuna_filtro.text != "Todas las comunas":
            solicitudes = [
                item for item in solicitudes
                if item[9] == self.comuna_filtro.text
            ]
        self.lista.values = tuple(
            f"#{item[0]} | {item[9]} | {item[10]} | {item[3]} | {item[5]}"
            for item in solicitudes
        )
        self.lista.text = "Selecciona una solicitud" if solicitudes else "No hay solicitudes"

    def aceptar(self, *_):
        solicitud_id, trabajador_id = self.seleccion()
        if solicitud_id is None or trabajador_id is None:
            self.aviso("Datos faltantes", "Selecciona una solicitud y un trabajador.")
            return
        aceptar_solicitud(solicitud_id, trabajador_id)
        self.aviso("Solicitud aceptada", "La solicitud fue asignada correctamente.")
        self.actualizar()

    def seleccion(self):
        if not self.solicitudes or self.lista.text.startswith(("Selecciona", "No hay")):
            return None, None
        if self.trabajadores.text.startswith(("Selecciona", "No hay")):
            return None, None
        solicitud_id = int(self.lista.text.split("|")[0].replace("#", "").strip())
        trabajador_id = int(self.trabajadores.text.split("|")[0].strip())
        return solicitud_id, trabajador_id

    def reasignar(self, *_):
        solicitud_id, trabajador_id = self.seleccion()
        if solicitud_id is None or trabajador_id is None:
            self.aviso("Datos faltantes", "Selecciona una solicitud y el nuevo trabajador.")
            return
        if reasignar_solicitud(solicitud_id, trabajador_id):
            self.aviso("Solicitud reasignada", "La solicitud fue asignada al nuevo trabajador.")
            self.actualizar()
        else:
            self.aviso("Error", "No se encontró la solicitud.")

    def eliminar(self, *_):
        if not self.solicitudes or self.lista.text.startswith(("Selecciona", "No hay")):
            self.aviso("Datos faltantes", "Selecciona una solicitud.")
            return
        solicitud_id = int(self.lista.text.split("|")[0].replace("#", "").strip())
        if eliminar_solicitud(solicitud_id):
            self.lista.text = "Selecciona una solicitud"
            self.actualizar()
            self.aviso("Solicitud eliminada", "La solicitud fue eliminada correctamente.")
        else:
            self.aviso("Error", "No se encontró la solicitud.")

    def agregar_trabajador(self, *_):
        layout = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(10))
        nombre = campo("Nombre completo")
        correo = campo("Correo")
        password = campo("Contraseña", password=True)
        guardar = boton("GUARDAR TRABAJADOR", VERDE)
        for widget in (nombre, correo, password, guardar):
            layout.add_widget(widget)
        popup = popup_estilizado("Nuevo trabajador", layout, 0.9, 0.65)

        def guardar_trabajador(*_):
            if not all((nombre.text.strip(), correo.text.strip(), password.text)):
                self.aviso("Datos faltantes", "Completa todos los campos.")
                return
            try:
                crear_trabajador(nombre.text.strip(), correo.text.strip(), password.text)
            except ValueError as error:
                self.aviso("No se pudo guardar", str(error))
                return
            popup.dismiss()
            self.actualizar()
            self.aviso("Trabajador agregado", "Ya está disponible para asignar solicitudes.")

        guardar.bind(on_release=guardar_trabajador)
        popup.open()

    def gestionar_trabajadores(self, *_):
        layout = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(10))
        trabajadores = selector("Selecciona un trabajador")
        layout.add_widget(Image(
            source="assets/hoja-temuco.png",
            fit_mode="contain",
            size_hint_y=None,
            height=dp(75),
        ))
        layout.add_widget(trabajadores)
        eliminar = boton("ELIMINAR TRABAJADOR", ROJO)
        agregar = boton("AGREGAR TRABAJADOR", VERDE)
        layout.add_widget(eliminar)
        layout.add_widget(agregar)
        popup = popup_estilizado("Trabajadores", layout, 0.92, 0.65)

        def cargar():
            disponibles = obtener_trabajadores()
            trabajadores.values = tuple(
                f"{item[0]} | {item[1]} | {item[2]}"
                for item in disponibles
            )
            trabajadores.text = "Selecciona un trabajador" if disponibles else "No hay trabajadores"

        def borrar(*_):
            if trabajadores.text.startswith("Selecciona") or trabajadores.text.startswith("No hay"):
                self.aviso("Datos faltantes", "Selecciona un trabajador.")
                return
            trabajador_id = int(trabajadores.text.split("|")[0].strip())
            try:
                eliminar_trabajador(trabajador_id)
            except ValueError as error:
                self.aviso("No se puede eliminar", str(error))
                return
            cargar()
            self.actualizar()
            popup.dismiss()
            self.aviso("Trabajador eliminado", "El trabajador fue eliminado correctamente.")

        eliminar.bind(on_release=borrar)
        agregar.bind(on_release=lambda *_: (popup.dismiss(), self.agregar_trabajador()))
        cargar()
        popup.open()


class TrabajadorScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = self.contenido("Panel del trabajador")
        self.solicitudes = []
        self.comuna_filtro = selector("Todas mis comunas")
        self.comuna_filtro.values = ("Todas mis comunas",) + COMUNAS
        self.comuna_filtro.bind(text=lambda *_: self.mostrar_solicitudes())
        self.lista = selector("Selecciona un retiro")
        filtros = BoxLayout(orientation="vertical", spacing=dp(10))
        filtros.add_widget(self.comuna_filtro)
        filtros.add_widget(self.lista)
        self.layout.add_widget(panel(filtros, 115))
        for texto, color, accion in (("ACTUALIZAR RETIROS", VERDE_CLARO, self.actualizar), ("MARCAR COMO REALIZADO", VERDE, self.realizado), ("MARCAR NO REALIZADO / PENDIENTE", NARANJA, self.no_realizado), ("CERRAR SESIÓN", ROJO, lambda *_: MDApp.get_running_app().cerrar_sesion())):
            accion_boton = boton(texto, color)
            accion_boton.bind(on_release=accion)
            self.layout.add_widget(accion_boton)
        self.add_widget(self.desplazar(self.layout))

    def actualizar(self, *_):
        usuario = MDApp.get_running_app().usuario
        self.solicitudes = obtener_solicitudes_trabajador(usuario[0])
        self.mostrar_solicitudes()

    def mostrar_solicitudes(self):
        solicitudes = self.solicitudes
        if self.comuna_filtro.text != "Todas mis comunas":
            solicitudes = [
                item for item in solicitudes
                if item[9] == self.comuna_filtro.text
            ]
        self.lista.values = tuple(
            f"#{item[0]} | {item[9]} | {item[10]} | {item[3]} | {item[5]}"
            for item in solicitudes
        )
        self.lista.text = "Selecciona un retiro" if solicitudes else "No tienes solicitudes asignadas"

    def realizado(self, *_):
        if not self.solicitudes or self.lista.text.startswith("Selecciona"):
            self.aviso("Datos faltantes", "Selecciona un retiro.")
            return
        solicitud_id = int(self.lista.text.split("|")[0].replace("#", "").strip())
        actualizar_solicitud_trabajador(solicitud_id, "Realizado", "Retiro completado")
        self.aviso("Retiro", "La solicitud fue marcada como realizada.")
        self.actualizar()

    def no_realizado(self, *_):
        if not self.solicitudes or self.lista.text.startswith("Selecciona"):
            self.aviso("Datos faltantes", "Selecciona un retiro.")
            return
        solicitud_id = int(self.lista.text.split("|")[0].replace("#", "").strip())
        actualizar_solicitud_trabajador(
            solicitud_id,
            "Pendiente - No realizado",
            "No fue posible realizar el retiro por un inconveniente.",
        )
        self.aviso("Solicitud pendiente", "El retiro quedó pendiente para revisión.")
        self.actualizar()


class TemucoRetiraApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.primary_hue = "700"
        self.theme_cls.theme_style = "Light"
        crear_tablas()
        crear_usuarios_iniciales()
        self.usuario = None
        manager = ScreenManager()
        manager.add_widget(LoginScreen(name="login"))
        manager.add_widget(CiudadanoScreen(name="ciudadano"))
        manager.add_widget(AdminScreen(name="admin"))
        manager.add_widget(TrabajadorScreen(name="trabajador"))
        self.manager = manager
        return manager

    def cargar_pantalla(self, nombre):
        self.manager.current = nombre

    def cerrar_sesion(self):
        self.usuario = None
        self.manager.current = "login"


if __name__ == "__main__":
    TemucoRetiraApp().run()