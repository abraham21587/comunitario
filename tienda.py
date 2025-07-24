import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Archivos
archivo_ventas = "ventas.xlsx"
archivo_clientes = "clientes.xlsx"

# Columnas esperadas
columnas_ventas = [
    "# de pedido", "Fecha", "Cliente", "Vendedor", "Producto",
    "Cantidad", "Total", "PagoCon", "Devuelta"
]
columnas_clientes = [
    "ID", "NOMBRE Y APELLIDO COMPLETO", "TIPO(1)", "NUMERO",
    "TELEFONO CONTACTO", "BARRIO Y/O DIRRECCION", "COMUNA", "DIAS QUE VINO"
]

# Validar y cargar archivo de ventas
if os.path.exists(archivo_ventas):
    try:
        df_ventas = pd.read_excel(archivo_ventas)
        if df_ventas.empty or any(col not in df_ventas.columns for col in columnas_ventas):
            df_ventas = pd.DataFrame(columns=columnas_ventas)
            df_ventas.to_excel(archivo_ventas, index=False)
    except:
        df_ventas = pd.DataFrame(columns=columnas_ventas)
        df_ventas.to_excel(archivo_ventas, index=False)
else:
    df_ventas = pd.DataFrame(columns=columnas_ventas)
    df_ventas.to_excel(archivo_ventas, index=False)

# Validar y cargar archivo de clientes
if os.path.exists(archivo_clientes):
    try:
        df_clientes = pd.read_excel(archivo_clientes)
    except:
        df_clientes = pd.DataFrame(columns=columnas_clientes)
        df_clientes.to_excel(archivo_clientes, index=False)
else:
    df_clientes = pd.DataFrame(columns=columnas_clientes)
    df_clientes.to_excel(archivo_clientes, index=False)

# Configurar Streamlit
st.set_page_config(page_title="Cajero Surtitienda Comunitaria", layout="centered")

menu = st.sidebar.radio("Menú", ["Registrar Venta", "Registrar Cliente", "Eliminar Venta", "Premios", "Resumen de Ventas"])

# === REGISTRAR CLIENTE ===
if menu == "Registrar Cliente":
    st.title("🧑‍💼 Registro de Clientes")
    with st.form("form_cliente"):
        nombre = st.text_input("Nombre y apellido completo")
        tipo = st.selectbox("Tipo de documento", ["CC", "TI"])
        numero = st.text_input("Número")
        telefono = st.text_input("Teléfono de contacto")
        barrio = st.text_input("Barrio y/o dirección")
        comuna = st.text_input("Comuna")
        enviar = st.form_submit_button("Guardar cliente")

    if enviar:
        if nombre and telefono:
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
                st.success("✅ Cliente registrado correctamente.")
        else:
            st.error("❌ Por favor completa los campos obligatorios.")

# === REGISTRAR VENTA ===
elif menu == "Registrar Venta":
    st.title("🧾 Registrar Venta")

    opciones_clientes = df_clientes["NOMBRE Y APELLIDO COMPLETO"].dropna().tolist()
    cliente = st.selectbox("Selecciona cliente", opciones_clientes) if opciones_clientes else None

    if cliente:
        vendedor = st.selectbox("Vendedor", ["Jairo", "Estefanía"])
        cantidad = st.number_input("Cantidad", min_value=1, step=1)
        precio = 2500
        total = cantidad * precio
        pago = st.number_input("Pago con", min_value=0, step=500)
        devuelta = max(0, pago - total)

        st.write(f"💰 Total: ${total:,.0f}")
        st.write(f"💵 Devuelta: ${devuelta:,.0f}")

        if st.button("Registrar venta"):
            nuevo_pedido = 1 if df_ventas.empty else df_ventas["# de pedido"].max() + 1
            nueva_venta = pd.DataFrame([{
                "# de pedido": nuevo_pedido,
                "Fecha": datetime.now().strftime("%Y-%m-%d"),
                "Cliente": cliente,
                "Vendedor": vendedor,
                "Producto": "Almuerzo",
                "Cantidad": cantidad,
                "Total": total,
                "PagoCon": pago,
                "Devuelta": devuelta
            }])
            df_ventas = pd.concat([df_ventas, nueva_venta], ignore_index=True)
            df_ventas.to_excel(archivo_ventas, index=False)

            idx = df_clientes[df_clientes["NOMBRE Y APELLIDO COMPLETO"] == cliente].index
            if not idx.empty:
                df_clientes.loc[idx, "DIAS QUE VINO"] += 1
                df_clientes.to_excel(archivo_clientes, index=False)

            st.success(f"✅ Venta registrada para {cliente}.")

# === ELIMINAR VENTA ===
elif menu == "Eliminar Venta":
    st.title("🗑️ Eliminar Venta")
    if not df_ventas.empty:
        df_ventas["Descripción"] = df_ventas.apply(
            lambda row: f"#{row['# de pedido']} - {row['Cliente']} ({row['Fecha']}) x{row['Cantidad']}", axis=1)
        seleccion = st.selectbox("Selecciona una venta", df_ventas["Descripción"].tolist())

        if seleccion:
            pedido_id = int(seleccion.split("-")[0].replace("#", "").strip())
            venta = df_ventas[df_ventas["# de pedido"] == pedido_id].iloc[0]
            cliente = venta["Cliente"]
            st.markdown(f"**Cliente:** {cliente}")
            st.markdown(f"**Cantidad:** {venta['Cantidad']}")
            st.markdown(f"**Total:** ${venta['Total']:,.0f}")
            st.markdown(f"**Fecha:** {venta['Fecha']}")

            if st.button("❌ Confirmar eliminación"):
                df_ventas = df_ventas[df_ventas["# de pedido"] != pedido_id].drop(columns=["Descripción"])
                df_ventas.to_excel(archivo_ventas, index=False)

                idx = df_clientes[df_clientes["NOMBRE Y APELLIDO COMPLETO"] == cliente].index
                if not idx.empty:
                    df_clientes.loc[idx, "DIAS QUE VINO"] = max(0, df_clientes.loc[idx, "DIAS QUE VINO"].values[0] - 1)
                    df_clientes.to_excel(archivo_clientes, index=False)

                st.success("✅ Venta eliminada correctamente.")
    else:
        st.info("No hay ventas registradas aún.")

# === PREMIOS ===
elif menu == "Premios":
    st.title("🎁 Premios por Almuerzos Comprados")
    if "Cliente" in df_ventas.columns:
        resumen = df_ventas.groupby("Cliente")["Cantidad"].sum().reset_index()
        resumen["Almuerzos Comprados"] = resumen["Cantidad"]
        resumen["Premios Ganados"] = resumen["Almuerzos Comprados"] // 30
        st.dataframe(resumen[["Cliente", "Almuerzos Comprados", "Premios Ganados"]].sort_values(by="Almuerzos Comprados", ascending=False))
    else:
        st.error("❌ El archivo de ventas no contiene la columna 'Cliente'. No se puede calcular premios.")

# === RESUMEN DE VENTAS ===
elif menu == "Resumen de Ventas":
    st.title("📜 Resumen de Ventas")
    if not df_ventas.empty:
        st.dataframe(df_ventas)
        total_general = df_ventas["Total"].sum()
        st.success(f"🧾 Total acumulado: **${total_general:,.0f}**")
    else:
        st.info("No hay ventas registradas.")
