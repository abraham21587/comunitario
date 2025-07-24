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
    if "Cliente" not in df_ventas.columns:
        df_ventas["Cliente"] = ""
        df_ventas.to_excel(archivo_ventas, index=False)

# Crear archivo de clientes si no existe
if not os.path.exists(archivo_clientes):
    df_clientes = pd.DataFrame(columns=columnas_clientes)
    df_clientes.to_excel(archivo_clientes, index=False)
else:
    df_clientes = pd.read_excel(archivo_clientes)

# Configurar página
st.set_page_config(page_title="🥘 Cajero Surtitienda Comunitaria", layout="centered")
menu = st.sidebar.radio("📋 Menú", [
    "Registrar Venta", "Registrar Cliente", 
    "Actualizar/Eliminar Cliente", "Premios", "Resumen de Ventas"
])

# ---------- REGISTRAR CLIENTE ----------
if menu == "Registrar Cliente":
    st.title("📇 Registro de Clientes")
    with st.form("form_cliente"):
        nombre = st.text_input("👤 Nombre y apellido completo") or "N/A"
        tipo = st.selectbox("🔔 Tipo de documento", ["CC", "TI"])
        numero = st.text_input("🔢 Número") or "N/A"
        telefono = st.text_input("📞 Teléfono de contacto") or "N/A"
        barrio = st.text_input("📍 Barrio y/o dirección") or "N/A"
        comuna = st.text_input("🏡 Comuna") or "N/A"
        enviar = st.form_submit_button("📂 Guardar cliente")

    if enviar:
        duplicado = (
            nombre.strip().lower() in df_clientes["NOMBRE Y APELLIDO COMPLETO"].str.lower().values
            or numero.strip() in df_clientes["NUMERO"].astype(str).values
            or telefono.strip() in df_clientes["TELEFONO CONTACTO"].astype(str).values
        )
        if duplicado:
            st.error("⚠️ Cliente ya registrado.")
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

# ---------- REGISTRAR VENTA ----------
elif menu == "Registrar Venta":
    st.title("📄 Registrar Venta")
    opciones_clientes = df_clientes["NOMBRE Y APELLIDO COMPLETO"].dropna().tolist()
    cliente = st.selectbox("👤 Selecciona cliente", opciones_clientes) if opciones_clientes else None

    if cliente:
        vendedor = st.selectbox("👨‍💼 Vendedor", ["Jairo", "Estefanía"])
        cantidad = st.number_input("🍱 Cantidad de almuerzos", min_value=1, step=1)
        precio = 2500
        total = cantidad * precio
        pago = st.number_input("💵 Pago con", min_value=0, step=500)
        devuelta = max(0, pago - total)

        st.info(f"💰 Total a pagar: **${total:,.0f}**")
        st.info(f"🔁 Devuelta: **${devuelta:,.0f}**")

        if st.button("📂 Registrar venta"):
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

            st.success(f"✅ Venta registrada exitosamente para **{cliente}**.")

    # ---------- ELIMINAR VENTA ----------
    st.markdown("---")
    st.subheader("🗑️ Eliminar una venta")

    if not df_ventas.empty:
        df_ventas["Descripcion"] = df_ventas.apply(lambda row: f"#{row['# de pedido']} - {row.get('Cliente', 'Sin nombre')} ({row['Fecha']}) x{row['Cantidad']}", axis=1)
        opcion = st.selectbox("📦 Selecciona una venta para eliminar", df_ventas["Descripcion"])

        if opcion:
            pedido_id = int(opcion.split("-")[0].replace("#", "").strip())
            venta_detalle = df_ventas[df_ventas["# de pedido"] == pedido_id].iloc[0]

            st.markdown("### 🧾 Detalles de la venta seleccionada")
            st.markdown(f"**Cliente:** {venta_detalle.get('Cliente', 'Sin nombre')}")
            st.markdown(f"**Fecha:** {venta_detalle['Fecha']}")
            st.markdown(f"**Vendedor:** {venta_detalle['Vendedor']}")
            st.markdown(f"**Producto:** {venta_detalle['Producto']}")
            st.markdown(f"**Cantidad:** {venta_detalle['Cantidad']}")
            st.markdown(f"**Total:** ${venta_detalle['Total']:,.0f}")
            st.markdown(f"**Pagó con:** ${venta_detalle['PagoCon']:,.0f}")
            st.markdown(f"**Devuelta:** ${venta_detalle['Devuelta']:,.0f}")

            if st.button("❌ Eliminar venta seleccionada"):
                nombre_cliente = venta_detalle.get("Cliente", "").strip()
                df_ventas = df_ventas[df_ventas["# de pedido"] != pedido_id].drop(columns=["Descripcion"])
                df_ventas.to_excel(archivo_ventas, index=False)

                if nombre_cliente:
                    idx = df_clientes[df_clientes["NOMBRE Y APELLIDO COMPLETO"].str.strip() == nombre_cliente].index
                    if not idx.empty:
                        df_clientes.loc[idx, "DIAS QUE VINO"] -= 1
                        df_clientes["DIAS QUE VINO"] = df_clientes["DIAS QUE VINO"].clip(lower=0)
                        df_clientes.to_excel(archivo_clientes, index=False)

                st.success(f"✅ Venta con pedido #{pedido_id} eliminada correctamente.")

# ---------- PREMIOS ----------
elif menu == "Premios":
    st.title("🎁 Premios por Almuerzos Comprados")

    if "Cliente" in df_ventas.columns and "Cantidad" in df_ventas.columns:
        resumen = df_ventas.groupby("Cliente")["Cantidad"].sum().reset_index()
        resumen["Almuerzos Comprados"] = resumen["Cantidad"]
        resumen["Premios Ganados 🏆"] = resumen["Almuerzos Comprados"] // 30
        resumen = resumen[["Cliente", "Almuerzos Comprados", "Premios Ganados 🏆"]]
        st.dataframe(resumen.sort_values(by="Almuerzos Comprados", ascending=False))
    else:
        st.warning("⚠️ No hay datos suficientes para calcular premios.")

# ---------- RESUMEN DE VENTAS ----------
elif menu == "Resumen de Ventas":
    st.title("📊 Resumen de Ventas")
    st.dataframe(df_ventas)

    if "Fecha" in df_ventas.columns:
        df_ventas["Fecha"] = pd.to_datetime(df_ventas["Fecha"], errors='coerce')
        ventas_por_dia = df_ventas.groupby(df_ventas["Fecha"].dt.date)["Total"].sum()

        st.subheader("📈 Ventas por día")
        st.line_chart(ventas_por_dia)

        if not ventas_por_dia.empty:
            dia_max = ventas_por_dia.idxmax()
            dia_min = ventas_por_dia.idxmin()
            st.success(f"🗓️ Día con más ventas: **{dia_max}** - 💰 ${ventas_por_dia.max():,.0f}")
            st.info(f"🗓️ Día con menos ventas: **{dia_min}** - 💸 ${ventas_por_dia.min():,.0f}")

