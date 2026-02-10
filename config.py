from supabase import create_client, Client
import sys

# --- CONFIGURACIÓN BODEGA 2.0 (INTEGRIDAD MANTENIDA) ---
URL = "https://aznkqqrakzhvbtlnjaxz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6bmtxcXJha3podmJ0bG5qYXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjY4NTAsImV4cCI6MjA4NTU0Mjg1MH0.4LRC-DsHidHkYyS4CiLUy51r-_lEgGPMvKL7_DnJWFI"

def conectar():
    """Establece la conexión con Supabase con diagnóstico de arquitectura."""
    try:
        return create_client(URL, KEY)
    except Exception as e:
        arch = "32-bit" if sys.maxsize <= 2**31-1 else "64-bit"
        print(f"Error de conexión en entorno {arch}: {e}")
        return None