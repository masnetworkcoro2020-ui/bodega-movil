import streamlit as st

def mostrar(supabase):
    st.header("📦 Gestión de Inventario")
    st.write("Módulo en mantenimiento - Próximamente escáner rápido.")
    
    # Botón de prueba para ver si carga
    if st.button("Probar conexión"):
        st.success("Conexión con el módulo exitosa")
