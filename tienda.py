# Surtitienda Comunitaria - App Mejorada

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# Archivos
archivo_ventas = "ventas.xlsx"
archivo_clientes = "clientes.xlsx"

# Columnas esperadas
columnas_clientes = [
    "ID", "NOMBRE Y APELLIDO COMPLETO", "TIPO(1)", "NUMERO",
    "TELEFONO CONTACTO", "BARRIO Y/O DIRRECCION", "COMUNA", "DIAS QUE VINO"
]

# Crear archivos si no existen
def cargar_datos():
    if not os.path.exists(archivo_clientes):
        pd.DataFrame(columns=columnas_clientes).to_excel(archivo_clientes, index=False)
    if not os.path.exists(archivo_ventas):
        pd.DataFrame(columns=["# de pedido", "Fecha", "Cliente", "Vendedor", "Producto", "Cantidad", "Total", "PagoCon", "Devuelta"]).to_excel(archivo_ventas, index=False)

    return pd.read_excel(archivo_clientes), pd.read_excel(archivo_ventas)

df_clientes, df_ventas = cargar_datos()

# Guardado
def guardar_clientes():
    df_clientes.to_excel(archivo_clientes, index=False)

def guardar_ventas():
    df_ventas.to_excel(archivo_ventas, index=False)

# Configurar página
st.set_page_config(page_title="Surtitienda Comunitaria", layout="centered")
menu = st.sidebar.radio("Menú", [
    "Registrar Venta", "Registrar Cliente", "Actualizar / Eliminar Cliente",
    "Resumen de Ventas", "Premios 🎁"
])

# === REGISTRAR CLIENTE ===
if menu == "Registrar Cliente":
    st.title("🧑‍💼 Registro de Clientes")
    with st.form("form_cliente"):
        nombre = st.text_input("Nombre y apellido completo")
        tipo = st.selectbox("Tipo de documento", ["CC", "TI"])
        numero = st.text_input("Número") or "N/A"
        telefono = st.text_input("Teléfono de contacto") or "N/A"
        barrio = st.text_input("Barrio y/o dirección") or "N/A"
        comuna = st.text_input("Comuna") or "N/A"
        enviar = st.form_submit_button("Guardar cliente")

    if enviar:
        if nombre:
            if nombre.strip().lower() in df_clientes["NOMBRE Y APELLIDO COMPLETO"].str.strip().str.lower().values:
                st.error("❌ Ya existe un cliente con ese nombre.")
            elif numero.strip() != "N/A" and numero.strip() in df_clientes["NUMERO"].astype(str).str.strip().values:
                st.error("❌ Ya existe un cliente con ese número.")
            elif telefono.strip() != "N/A" and telefono.strip() in df_clientes["TELEFONO CONTACTO"].astype(str).str.strip().values:
                st.error("❌ Ya existe un cliente con ese teléfono.")
            else:
                nuevo_id = 1 if df_clientes.empty else df_clientes["ID"].max() + 1
                nuevo = pd.DataFrame([{
                    "ID": nuevo_id,
                    "NOMBRE Y APELLIDO COMPLETO": nombre,
                    "TIPO(1)": tipo,
                    "NUMERO": numero,
                    "TELEFONO CONTACTO": telefono,
                    "BARRIO Y/O DIRRECCION": barrio,
                    "COMUNA": comuna,
                    "DIAS QUE VINO": 0
                }])
                df_clientes = pd.concat([df_clientes, nuevo], ignore_index=True)
                guardar_clientes()
                st.success("✅ Cliente registrado correctamente.")
        else:
            st.error("Por favor completa el nombre del cliente.")

    if st.button("📋 Mostrar clientes registrados"):
        st.dataframe(df_clientes)

# === REGISTRAR VENTA ===
elif menu == "Registrar Venta":
    st.title("🧾 Registrar Venta")
    clientes = df_clientes["NOMBRE Y APELLIDO COMPLETO"].dropna().tolist()
    cliente = st.selectbox("Cliente", clientes)

    if cliente:
        vendedor = st.selectbox("Vendedor", ["Jairo", "Estefanía", "Otra persona"])
        cantidad = st.number_input("Cantidad de almuerzos", min_value=1, step=1)
        precio = 2500
        total = cantidad * precio
        pago = st.number_input("Pago con:", min_value=0)
        devuelta = pago - total if pago >= total else 0
        st.write(f"💰 Total: ${total:,.0f}")
        st.write(f"💵 Devuelta: ${devuelta:,.0f}")

        if st.button("Registrar venta"):
            if pago < total:
                st.error("Pago insuficiente.")
            else:
                pedido = 1 if df_ventas.empty else df_ventas["# de pedido"].max() + 1
                venta = pd.DataFrame([{
                    "# de pedido": pedido,
                    "Fecha": datetime.now().strftime("%Y-%m-%d"),
                    "Cliente": cliente,
                    "Vendedor": vendedor,
                    "Producto": "Almuerzo",
                    "Cantidad": cantidad,
                    "Total": total,
                    "PagoCon": pago,
                    "Devuelta": devuelta
                }])
                df_ventas = pd.concat([df_ventas, venta], ignore_index=True)
                guardar_ventas()

                idx = df_clientes[df_clientes["NOMBRE Y APELLIDO COMPLETO"] == cliente].index
                if not idx.empty:
                    df_clientes.loc[idx, "DIAS QUE VINO"] += 1
                    guardar_clientes()
                st.success(f"✅ Venta registrada. Pedido #{pedido}")

    st.markdown("---")
    st.subheader("🗑️ Eliminar Compra")
    pedidos_disponibles = df_ventas["# de pedido"].tolist()
    pedido_seleccionado = st.selectbox("Selecciona un pedido", pedidos_disponibles)
    pedido_info = df_ventas[df_ventas["# de pedido"] == pedido_seleccionado]
    st.write("Detalles del pedido:")
    st.dataframe(pedido_info)

    if st.button("Eliminar compra"):
        df_ventas = df_ventas[df_ventas["# de pedido"] != pedido_seleccionado]
        guardar_ventas()
        st.success("Compra eliminada correctamente.")

# === RESUMEN DE VENTAS ===
elif menu == "Resumen de Ventas":
    st.title("📊 Resumen de Ventas")
    st.dataframe(df_ventas)
    total_general = df_ventas["Total"].sum()
    st.success(f"🧾 Total acumulado: ${total_general:,.0f}")

# === PREMIOS ===
elif menu == "Premios 🎁":
    st.title("🎁 Clientes Premiados por Asistencia Consecutiva")

    def dias_consecutivos(fecha_lista):
        fechas = sorted([datetime.strptime(f, "%Y-%m-%d") for f in fecha_lista])
        max_consec = actual = 1
        for i in range(1, len(fechas)):
            if (fechas[i] - fechas[i-1]).days == 1:
                actual += 1
                max_consec = max(max_consec, actual)
            else:
                actual = 1
        return max_consec

    premiados = []
    for cliente in df_clientes["NOMBRE Y APELLIDO COMPLETO"]:
        fechas = df_ventas[df_ventas["Cliente"] == cliente]["Fecha"].tolist()
        if len(fechas) >= 15:
            consecutivos = dias_consecutivos(fechas)
            if consecutivos >= 15:
                premiados.append((cliente, consecutivos))

    premiados.sort(key=lambda x: x[1], reverse=True)

    if premiados:
        df_premios = pd.DataFrame(premiados, columns=["Cliente", "Días consecutivos"])
        st.dataframe(df_premios)
    else:
        st.info("Ningún cliente ha asistido 15 días consecutivos aún.")

