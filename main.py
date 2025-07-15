import flet as ft
import json
from datetime import date
import os


DB_FILE = "data.json"
TAREAS = [
    "Cuadrar recaudaciones",
    "Actualizar planilla de cierre diario",
    "Cierre de turno en copec fuel",
    "Enviar cuadre de promae",
    "Actualizar planilla de stock Bluemax",
    "Cierre diario de Dinamo",
    "Cierre diario de stock combustibles",
    "Registrar facturas en stock no combustibles",
    "Ingresar pedido de Bluemax granel",
    "Enviar documentos de Bluemax granel recepcionado",
    "Solicitar factura para clientes",
    "Ingresar denuncias por robos declarados",
    "Ingresar llamanos por robos declarados",
    "Enviar respaldos de robos declarados",
    "Enviar AADD pendientes por correo",
    "Cargar documentos fisicos en Google Drive",
    "Cierre semanal de temporis",
    "Actualizacion semanal de precios combustibles"
]


def cargar_datos():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump({}, f)
    with open(DB_FILE, "r") as f:
        return json.load(f)


def guardar_datos(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)


def main(page: ft.Page):
    page.title = "Checklist Diario"
    page.scroll = ft.ScrollMode.AUTO
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 10
    page.window_width = 400
    page.window_height = 800

    datos = cargar_datos()
    selected_date = date.today().isoformat()
    checkboxes = []
    observaciones = {}

    solo_lectura = ft.Text(value="")

    def cargar_fecha(e=None):
        nonlocal selected_date
        selected_date = fecha_field.value

        solo_lectura.value = ""

        if selected_date in datos:
            entry = datos[selected_date]
            for t, cb in zip(TAREAS, checkboxes):
                cb.value = entry["tareas"].get(t, False)
                observaciones[t].value = entry["observaciones"].get(t, "")
        else:
            for cb in checkboxes:
                cb.value = False
            for obs in observaciones.values():
                obs.value = ""

        if selected_date != date.today().isoformat():
            for cb in checkboxes:
                cb.disabled = True
            for obs in observaciones.values():
                obs.read_only = True
            btn_guardar.visible = False
            solo_lectura.value = "🔒 Modo solo lectura (no editable)"
        else:
            for cb in checkboxes:
                cb.disabled = False
            for obs in observaciones.values():
                obs.read_only = False
            btn_guardar.visible = True
            solo_lectura.value = ""

        page.update()

    def guardar_click(e):
        if selected_date != date.today().isoformat():
            return
        tareas_estado = {t: cb.value for t, cb in zip(TAREAS, checkboxes)}
        obs = {
            t: observaciones[t].value for t in TAREAS if observaciones[t].value}
        datos[selected_date] = {"tareas": tareas_estado, "observaciones": obs}
        guardar_datos(datos)

        # 🧹 Limpiar campos tras guardar
        for cb in checkboxes:
            cb.value = False
        for obs in observaciones.values():
            obs.value = ""

        page.snack_bar = ft.SnackBar(
            ft.Text("✅ Jornada guardada y checklist limpiado"))
        page.snack_bar.open = True
        page.update()

    fecha_field = ft.TextField(
        label="Fecha (YYYY-MM-DD)",
        value=selected_date,
        on_submit=cargar_fecha,
        keyboard_type=ft.KeyboardType.DATETIME
    )

    btn_refrescar = ft.ElevatedButton(
        "🔄 Refrescar fecha", on_click=cargar_fecha)

    page.add(ft.Row([fecha_field, btn_refrescar], wrap=True))
    page.add(solo_lectura)

    for tarea in TAREAS:
        cb = ft.Checkbox(label=tarea, scale=0.9)
        obs = ft.TextField(
            label=f"Observación: {tarea}",
            multiline=True,
            max_lines=2,
            expand=True,
            dense=True
        )
        checkboxes.append(cb)
        observaciones[tarea] = obs
        page.add(ft.Column([cb, obs], spacing=5))

    btn_guardar = ft.ElevatedButton("Guardar jornada", on_click=guardar_click)
    page.add(btn_guardar)


# 🚨 PARA RENDER
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    ft.app(target=main, view=ft.WEB_BROWSER, port=port)
