import flet as ft
from supabase import create_client
from flet_barcode_reader import BarcodeReader

# --- CONFIGURACIÓN DE TU BASE DE DATOS ---
URL_SUPABASE = "TU_URL_DE_SUPABASE_AQUÍ"
KEY_SUPABASE = "TU_ANON_KEY_DE_SUPABASE_AQUÍ"
supabase = create_client(URL_SUPABASE, KEY_SUPABASE)

def main(page: ft.Page):
    page.title = "Inventario Móvil"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = "always"
    page.padding = 20

    # Funciones de lógica de negocio (Tu ID:1 original)
    def obtener_tasa_db():
        try:
            res = supabase.table("ajustes").select("valor").eq("id", 1).execute()
            return float(res.data[0]['valor']) if res.data else 40.0
        except: return 40.0

    def recalcular(e):
        try:
            t = obtener_tasa_db()
            m = float(ent_margen.value or 0) / 100
            
            # Lógica 360° para móvil
            if e.control == ent_cbs:
                cbs = float(ent_cbs.value or 0)
                cusd = cbs / t
                vusd = cusd * (1 + m)
                vbs = vusd * t
                ent_cusd.value = f"{cusd:.2f}"
                ent_vusd.value = f"{vusd:.2f}"
                ent_vbs.value = f"{vbs:.2f}"
            
            page.update()
        except: pass

    # --- COMPONENTES DE LA INTERFAZ ---
    ent_cod = ft.TextField(label="Código de Barras", expand=True)
    
    # Función para el escáner del teléfono
    def on_scan(e):
        ent_cod.value = e.data
        page.update()

    ent_nom = ft.TextField(label="Producto (Nombre)")
    ent_cbs = ft.TextField(label="Costo Bs (Fijo)", bgcolor="#fcf3cf", color="black", on_change=recalculate)
    ent_cusd = ft.TextField(label="Costo $", bgcolor="#ebedef", color="black")
    ent_margen = ft.TextField(label="Margen %", value="25")
    ent_vusd = ft.TextField(label="Venta $")
    ent_vbs = ft.TextField(label="Venta Bs (Móvil)", bgcolor="#d4efdf", color="black", weight="bold")

    def guardar_en_supabase(e):
        try:
            datos = {
                "codigo": ent_cod.value.strip().upper(),
                "nombre": ent_nom.value.strip().upper(),
                "costo_usd": float(ent_cusd.value or 0),
                "costo_bs": float(ent_cbs.value or 0),
                "margen": float(ent_margen.value or 25),
                "venta_usd": float(ent_vusd.value or 0),
                "venta_bs": float(ent_vbs.value or 0)
            }
            # Intentar guardar por 'codigo' o 'código' como en tu original
            try:
                supabase.table("productos").upsert(datos, on_conflict="codigo").execute()
            except:
                datos["código"] = datos.pop("codigo")
                supabase.table("productos").upsert(datos, on_conflict="código").execute()
            
            page.snack_bar = ft.SnackBar(ft.Text("✅ Guardado en Supabase"))
            page.snack_bar.open = True
            page.update()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"❌ Error: {ex}"))
            page.snack_bar.open = True
            page.update()

    # --- DISEÑO ---
    page.add(
        ft.Text("📦 REPOSICIÓN MÓVIL", size=28, weight="bold"),
        ft.Divider(),
        # Botón que activa la cámara del cel
        BarcodeReader(on_scan=on_scan), 
        ent_cod,
        ent_nom,
        ft.Row([ent_cbs, ent_cusd]),
        ent_margen,
        ft.Row([ent_vusd, ent_vbs]),
        ft.ElevatedButton(
            "💾 GUARDAR PRODUCTO", 
            on_click=guardar_en_supabase,
            bgcolor=ft.colors.GREEN_800,
            color=ft.colors.WHITE,
            width=500, height=60
        )
    )

ft.app(target=main)
