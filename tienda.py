# cajero_surtitienda.py
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
    df_ventas.columns = df_ventas.columns.str.strip().str.lower()
    if "cliente" not in df_ventas.columns:
        df_ventas["cliente"] = ""
        df_ventas.to_excel(archivo_ventas, index=False)

# Crear archivo de clientes si no existe
if not os.path.exists(archivo_clientes):
    df_clientes = pd.DataFrame(columns=columnas_clientes)
    df_clientes.to_excel(archivo_clientes, index=False)
else:
    df_clientes = pd.read_excel(archivo_clientes)

# Configurar pagina
st.set_page_config(page_title="Cajero Surtitienda Comunitaria", layout="centered")
menu = st.sidebar.radio("Menú", ["Registrar Venta", "Registrar Cliente", "Premios", "Resumen de Ventas"])

# Registrar Cliente
if menu == "Registrar Cliente":
    st.title("Registro de Clientes")
    with st.form("form_cliente"):
        nombre = st.text_input("Nombre y apellido completo") or "N/A"
        tipo = st.selectbox("Tipo de documento", ["CC", "TI"])
        numero = st.text_input("Número") or "N/A"
        telefono = st.text_input("Teléfono de contacto") or "N/A"
        barrio = st.text_input("Barrio y/o dirección") or "N/A"
        comuna = st.text_input("Comuna") or "N/A"
        enviar = st.form_submit_button("Guardar cliente")

    if enviar:
        duplicado = (
            nombre.strip().lower() in df_clientes["NOMBRE Y APELLIDO COMPLETO"].str.lower().values
            or numero.strip() in df_clientes["NUMERO"].astype(str).values
            or telefono.strip() in df_clientes["TELEFONO CONTACTO"].astype(str).values
        )
        if duplicado:
            st.error("Cliente ya registrado.")
        else:
            nuevo_id = 1 if df_clientes.empty else df_clientes["ID"].max() + 1
            nuevo_cliente = pd.DataFrame([{
                "ID": nuevo_id,
                "NOMBRE Y APELLIDO COMPLETO": nombre,
                "TIPO(1)": tipo,
                "NUMERO": numero,
                "TELEFONO CONTACTO": telefono,
                "BARRIO Y/O DIRRECCION": barrio,
                "COMUNA": comuna,
                "DIAS QUE VINO": 0
            }])
            df_clientes = pd.concat([df_clientes, nuevo_cliente], ignore_index=True)
            df_clientes.to_excel(archivo_clientes, index=False)
            st.success("Cliente registrado correctamente.")

# Registrar Venta
elif menu == "Registrar Venta":
    st.title("Registrar Venta")
    opciones_clientes = df_clientes["NOMBRE Y APELLIDO COMPLETO"].dropna().tolist()
    cliente = st.selectbox("Selecciona cliente", opciones_clientes) if opciones_clientes else None

    if cliente:
        vendedor = st.selectbox("Vendedor", ["Jairo", "Estefanía"])
        cantidad = st.number_input("Cantidad", min_value=1, step=1)
        precio = 2500
        total = cantidad * precio
        pago = st.number_input("Pago con", min_value=0, step=500)
        devuelta = max(0, pago - total)

        st.write(f"Total: ${total:,.0f}")
        st.write(f"Devuelta: ${devuelta:,.0f}")

        if st.button("Registrar venta"):
            nuevo_pedido = 1 if df_ventas.empty else df_ventas["# de pedido"].max() + 1
            nueva_venta = pd.DataFrame([{
                "# de pedido": nuevo_pedido,
                "fecha": datetime.now().strftime("%Y-%m-%d"),
                "cliente": cliente,
                "vendedor": vendedor,
                "producto": "Almuerzo",
                "cantidad": cantidad,
                "total": total,
                "pagocon": pago,
                "devuelta": devuelta
            }])
            df_ventas = pd.concat([df_ventas, nueva_venta], ignore_index=True)
            df_ventas.to_excel(archivo_ventas, index=False)

            idx = df_clientes[df_clientes["NOMBRE Y APELLIDO COMPLETO"] == cliente].index
            if not idx.empty:
                df_clientes.loc[idx, "DIAS QUE VINO"] += 1
                df_clientes.to_excel(archivo_clientes, index=False)

            st.success(f"Venta registrada para {cliente}.")

# Premios
elif menu == "Premios":
    st.title("🎁 Premios por Almuerzos Comprados")
    resumen = df_ventas.groupby("cliente")["cantidad"].sum().reset_index()
    resumen["premios ganados"] = resumen["cantidad"] // 30
    resumen["almuerzos comprados"] = resumen["cantidad"]
    resumen = resumen[["cliente", "almuerzos comprados", "premios ganados"]]
    resumen.columns = ["Cliente", "Almuerzos Comprados", "Premios Ganados"]
    st.dataframe(resumen.sort_values(by="Almuerzos Comprados", ascending=False))

# Resumen de Ventas
elif menu == "Resumen de Ventas":
    st.title("📊 Resumen de Ventas")
    st.dataframe(df_ventas)

    df_ventas["fecha"] = pd.to_datetime(df_ventas["fecha"], errors='coerce')
    ventas_por_dia = df_ventas.groupby(df_ventas["fecha"].dt.date)["total"].sum()

    st.subheader("📈 Ventas por día")
    st.line_chart(ventas_por_dia)

    if not ventas_por_dia.empty:
        dia_max = ventas_por_dia.idxmax()
        dia_min = ventas_por_dia.idxmin()
        st.success(f"Día con más ventas: {dia_max} - ${ventas_por_dia.max():,.0f}")
        st.warning(f"Día con menos ventas: {dia_min} - ${ventas_por_dia.min():,.0f}")
