import flet as ft
from supabase import create_client

# Configuración de Supabase (Reemplaza con tus credenciales)
URL = "TU_URL_DE_SUPABASE"
KEY = "TU_KEY_DE_SUPABASE"
supabase = create_client(URL, KEY)

def main(page: ft.Page):
    page.title = "Inventario Global"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = "always"

    # --- LÓGICA DE CÁLCULO (Tu lógica 360°) ---
    def obtener_tasa():
        try:
            res = supabase.table("ajustes").select("valor").eq("id", 1).execute()
            return float(res.data[0]['valor']) if res.data else 40.0
        except: return 40.0

    def recalcular(e):
        try:
            t = obtener_tasa()
            m = float(ent_margen.value or 0) / 100
            
            if e.control == ent_cbs:
                cbs = float(ent_cbs.value or 0)
                cusd = cbs / t
                vusd = cusd * (1 + m)
                vbs = vusd * t
                ent_cusd.value = f"{cusd:.2f}"
                ent_vusd.value = f"{vusd:.2f}"
                ent_vbs.value = f"{vbs:.2f}"
            # ... (Se repite la lógica para los demás campos)
            page.update()
        except: pass

    # --- INTERFAZ (Adaptada a pantalla de celular) ---
    ent_cod = ft.TextField(label="Código de Barras", expand=True)
    
    # Botón para activar cámara del celular (Solo funciona en Web/App)
    def escanear(e):
        # Aquí se integraría un plugin de cámara como flet_barcode_reader
        # Por ahora, simulamos la entrada para que veas la estructura
        page.snack_bar = ft.SnackBar(ft.Text("Abriendo cámara del teléfono..."))
        page.snack_bar.open = True
        page.update()

    ent_nom = ft.TextField(label="Producto")
    ent_cbs = ft.TextField(label="Costo Bs (Fijo)", bgcolor="#fcf3cf", color="black", on_change=recalcular)
    ent_cusd = ft.TextField(label="Costo $", bgcolor="#ebedef", color="black", on_change=recalcular)
    ent_margen = ft.TextField(label="Margen %", value="25", on_change=recalcular)
    ent_vusd = ft.TextField(label="Venta $", on_change=recalcular)
    ent_vbs = ft.TextField(label="Venta Bs (Móvil)", bgcolor="#d4efdf", color="black", weight="bold", on_change=recalcular)

    def guardar_datos(e):
        datos = {
            "codigo": ent_cod.value.upper(),
            "nombre": ent_nom.value.upper(),
            "costo_usd": float(ent_cusd.value or 0),
            "venta_usd": float(ent_vusd.value or 0)
        }
        supabase.table("productos").upsert(datos).execute()
        page.snack_bar = ft.SnackBar(ft.Text("¡Producto Guardado!"))
        page.snack_bar.open = True
        page.update()

    # Diseño visual
    page.add(
        ft.Text("📦 GESTIÓN DE INVENTARIO", size=24, weight="bold"),
        ft.Row([ent_cod, ft.IconButton(ft.icons.QR_CODE_SCANNER, on_click=escanear)]),
        ent_nom,
        ft.Row([ent_cbs, ent_cusd]),
        ent_margen,
        ft.Row([ent_vusd, ent_vbs]),
        ft.ElevatedButton("💾 GUARDAR / ACTUALIZAR", 
                         bgcolor=ft.colors.GREEN_700, 
                         color=ft.colors.WHITE,
                         on_click=guardar_datos,
                         width=400, height=50)
    )

ft.app(target=main, view=ft.AppView.WEB_BROWSER)
