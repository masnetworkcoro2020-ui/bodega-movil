import streamlit as st

st.set_page_config(page_title="Prueba de Motor")

st.title("🚀 Motor Principal Activo")
st.write("Mano, si lees esto, el error ya se fue.")

# ADN Maestro para probar
u = st.text_input("Usuario")
p = st.text_input("Clave", type="password")

if st.button("Probar Acceso"):
    if u == "jmaar" and p == "15311751":
        st.success("¡Acceso Maestro Confirmado!")
    else:
        st.error("Credenciales incorrectas")
