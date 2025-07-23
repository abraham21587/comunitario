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

# Crear archivo de clientes si no existe
if not os.path.exists(archivo_clientes):
    df_clientes = pd.DataFrame(columns=columnas_clientes)
    df_clientes.to_excel(archivo_clientes, index=False)
else:
    df_clientes = pd.read_excel(archivo_clientes)

# Configuración de la página
st.set_page_config(page_title="Cajero Surtitienda Comunitaria", layout="centered")

# Menú lateral
menu = st.sidebar.radio("Menú", ["Registrar Venta", "Registrar Cliente"])

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
            st.error("Por favor completa los campos obligatorios.")

    # Mostrar tabla de clientes existentes
    st.markdown("---")
    if st.button("📋 Mostrar clientes registrados"):
        if df_clientes.empty:
            st.info("No hay clientes registrados aún.")
        else:
            st.subheader("📄 Lista de clientes")
            st.dataframe(df_clientes)


# === REGISTRAR VENTA ===
if menu == "Registrar Venta":
    st.title("🧾 Cajero Surtitienda Comunitaria")
    st.markdown("Registra tus ventas diarias de almuerzos 🍽️")

    # Buscador de cliente
    st.subheader("👤 Buscar cliente")
    opciones_clientes = df_clientes["NOMBRE Y APELLIDO COMPLETO"].dropna().tolist()
    cliente_seleccionado = st.selectbox(
        "Selecciona el cliente",
        opciones_clientes,
        index=0 if opciones_clientes else None,
        placeholder="Escribe el nombre...",
    ) if opciones_clientes else None

    if cliente_seleccionado:
        st.markdown(f"🧍 **Cliente seleccionado:** `{cliente_seleccionado}`")

    # Registro de venta
    vendedor = st.selectbox("Selecciona el vendedor", ["Jairo", "Estefanía", "Otra persona"])
    producto = "Almuerzo"
    st.text_input("Producto", producto, disabled=True)

    cantidad = st.number_input("Cantidad de almuerzos", min_value=1, step=1)
    precio_unitario = 2500
    total = cantidad * precio_unitario
    st.write(f"💰 Total a pagar: **${total:,.0f}**")

    pago_con = st.number_input("Pago con:", min_value=0, step=1000)
    devuelta = pago_con - total if pago_con >= total else 0
    st.write(f"💵 Devuelta: **${devuelta:,.0f}**")

    if st.button("Registrar venta"):
        if pago_con < total:
            st.error("El valor pagado es insuficiente.")
        elif not cliente_seleccionado:
            st.error("Por favor selecciona un cliente.")
        else:
            # Registrar venta
            nuevo_pedido = 1 if df_ventas.empty else df_ventas["# de pedido"].max() + 1
            nueva_venta = pd.DataFrame([{
                "# de pedido": nuevo_pedido,
                "Fecha": datetime.now().strftime("%Y-%m-%d"),
                "Cliente": cliente_seleccionado,
                "Vendedor": vendedor,
                "Producto": producto,
                "Cantidad": cantidad,
                "Total": total,
                "PagoCon": pago_con,
                "Devuelta": devuelta
            }])
            df_ventas = pd.concat([df_ventas, nueva_venta], ignore_index=True)
            df_ventas.to_excel(archivo_ventas, index=False)

            # Aumentar "DIAS QUE VINO"
            idx = df_clientes[df_clientes["NOMBRE Y APELLIDO COMPLETO"] == cliente_seleccionado].index
            if not idx.empty:
                dias_actuales = df_clientes.loc[idx, "DIAS QUE VINO"].fillna(0).astype(int)
                df_clientes.loc[idx, "DIAS QUE VINO"] = dias_actuales + 1
                df_clientes.to_excel(archivo_clientes, index=False)

            st.success(f"✅ Venta registrada con pedido #{nuevo_pedido} para {cliente_seleccionado}.")

    # Resumen del día
    st.subheader("📊 Resumen del Día (solo hoy)")
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    df_hoy = df_ventas[df_ventas["Fecha"] == fecha_hoy]

    if not df_hoy.empty:
        total_dia = df_hoy["Total"].sum()
        st.metric("Total vendido hoy", f"${total_dia:,.0f}")
        st.bar_chart(df_hoy.groupby("Vendedor")["Total"].sum())

        if st.button("🛑 Cerrar caja"):
            st.subheader("📦 Caja cerrada")
            st.dataframe(df_hoy)
            st.success(f"💰 Total vendido hoy: **${total_dia:,.0f}**")
    else:
        st.info("No hay ventas registradas hoy.")

    # Resumen completo
    if st.button("📂 Ver resumen final"):
        st.subheader("📜 Resumen completo de ventas")
        st.dataframe(df_ventas)
        total_general = df_ventas["Total"].sum()
        st.success(f"🧾 Total acumulado: **${total_general:,.0f}**")
