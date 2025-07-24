import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Archivos
archivo_ventas = "ventas.xlsx"
archivo_clientes = "clientes.xlsx"

# Columnas esperadas en clientes
columnas_clientes = [
    "ID", "NOMBRE Y APELLIDO COMPLETO", "TIPO(1)", "NUMERO",
    "TELEFONO CONTACTO", "BARRIO Y/O DIRRECCION", "COMUNA", "DIAS QUE VINO"
]

# Crear archivo de ventas si no existe
if not os.path.exists(archivo_ventas):
    df_ventas = pd.DataFrame(columns=[
        "# de pedido", "Fecha", "Cliente", "Vendedor", "Producto",
        "Cantidad", "Total", "PagoCon", "Devuelta"
    ])
    df_ventas.to_excel(archivo_ventas, index=False)
else:
    df_ventas = pd.read_excel(archivo_ventas)
    if "Cliente" not in df_ventas.columns:
        df_ventas["Cliente"] = ""
        df_ventas.to_excel(archivo_ventas, index=False)

# Crear archivo de clientes si no existe
if not os.path.exists(archivo_clientes):
    df_clientes = pd.DataFrame(columns=columnas_clientes)
    df_clientes.to_excel(archivo_clientes, index=False)
else:
    df_clientes = pd.read_excel(archivo_clientes)

# Configuración de la página
st.set_page_config(page_title="Cajero Surtitienda Comunitaria", layout="centered")

# Menú lateral
menu = st.sidebar.radio("Menú", ["Registrar Venta", "Registrar Cliente", "Eliminar Venta", "Premios", "Resumen de Ventas"])

# === REGISTRAR CLIENTE ===
if menu == "Registrar Cliente":
    # ... (sin cambios)
    pass

# === REGISTRAR VENTA ===
elif menu == "Registrar Venta":
    # ... (sin cambios)
    pass

# === ELIMINAR VENTA ===
elif menu == "Eliminar Venta":
    st.title("🗑️ Eliminar Venta")
    if not df_ventas.empty:
        df_ventas["Descripción"] = df_ventas.apply(lambda x: f"#{x['# de pedido']} - {x['Cliente']} ({x['Fecha']}) x{x['Cantidad']}", axis=1)
        seleccion = st.selectbox("Selecciona una venta para ver detalles", df_ventas["Descripción"].tolist())

        if seleccion:
            pedido_id = int(seleccion.split("-")[0].replace("#", "").strip())
            venta = df_ventas[df_ventas["# de pedido"] == pedido_id].iloc[0]
            st.markdown(f"**Cliente:** {venta['Cliente']}")
            st.markdown(f"**Vendedor:** {venta['Vendedor']}")
            st.markdown(f"**Cantidad:** {venta['Cantidad']}")
            st.markdown(f"**Total:** ${venta['Total']:,.0f}")
            st.markdown(f"**Fecha:** {venta['Fecha']}")

            if st.button("Eliminar esta venta"):
                nombre_cliente = venta.get("Cliente", "")
                df_ventas = df_ventas[df_ventas["# de pedido"] != pedido_id].drop(columns=["Descripción"])
                df_ventas.to_excel(archivo_ventas, index=False)

                idx = df_clientes[df_clientes["NOMBRE Y APELLIDO COMPLETO"] == nombre_cliente].index
                if not idx.empty:
                    df_clientes.loc[idx, "DIAS QUE VINO"] -= 1
                    df_clientes["DIAS QUE VINO"] = df_clientes["DIAS QUE VINO"].clip(lower=0)
                    df_clientes.to_excel(archivo_clientes, index=False)

                st.success("✅ Venta eliminada correctamente.")
    else:
        st.info("No hay ventas para eliminar.")

# === PREMIOS ===
elif menu == "Premios":
    # ... (sin cambios)
    pass

# === RESUMEN DE VENTAS ===
elif menu == "Resumen de Ventas":
    st.title("📜 Resumen completo de ventas")
    if not df_ventas.empty:
        st.dataframe(df_ventas[["# de pedido", "Fecha", "Cliente", "Vendedor", "Producto", "Cantidad", "Total", "PagoCon", "Devuelta"]])
        total_general = df_ventas["Total"].sum()
        st.success(f"🧾 Total acumulado: **${total_general:,.0f}**")
    else:
        st.info("No hay ventas registradas.")

