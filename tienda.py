# Surtitienda Comunitaria - App con resumen gráfico y premios por compras

import streamlit as st
import pandas as pd
from datetime import datetime
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

    df_clientes = pd.read_excel(archivo_clientes)
    df_ventas = pd.read_excel(archivo_ventas)

    # Limpiar nombres de columnas
    df_clientes.columns = df_clientes.columns.str.strip()
    df_ventas.columns = df_ventas.columns.str.strip()

    return df_clientes, df_ventas

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

# === ACTUALIZAR / ELIMINAR CLIENTE ===
elif menu == "Actualizar / Eliminar Cliente":
    st.title("🛠️ Actualizar o Eliminar Cliente")
    if not df_clientes.empty:
        cliente_sel = st.selectbox("Selecciona un cliente", df_clientes["NOMBRE Y APELLIDO COMPLETO"].tolist())
        idx = df_clientes[df_clientes["NOMBRE Y APELLIDO COMPLETO"] == cliente_sel].index[0]

        with st.form("form_update"):
            nuevo_nombre = st.text_input("Nombre", df_clientes.loc[idx, "NOMBRE Y APELLIDO COMPLETO"])
            nuevo_tipo = st.selectbox("Tipo", ["CC", "TI"], index=["CC", "TI"].index(df_clientes.loc[idx, "TIPO(1)"]))
            nuevo_num = st.text_input("Número", df_clientes.loc[idx, "NUMERO"])
            nuevo_tel = st.text_input("Teléfono", df_clientes.loc[idx, "TELEFONO CONTACTO"])
            nuevo_barrio = st.text_input("Barrio", df_clientes.loc[idx, "BARRIO Y/O DIRRECCION"])
            nueva_comuna = st.text_input("Comuna", df_clientes.loc[idx, "COMUNA"])
            guardar = st.form_submit_button("Actualizar")

        if guardar:
            df_clientes.loc[idx] = [
                df_clientes.loc[idx, "ID"], nuevo_nombre, nuevo_tipo,
                nuevo_num, nuevo_tel, nuevo_barrio, nueva_comuna,
                df_clientes.loc[idx, "DIAS QUE VINO"]
            ]
            guardar_clientes()
            st.success("Cliente actualizado")

        if st.button("❌ Eliminar cliente"):
            df_clientes = df_clientes.drop(index=idx)
            guardar_clientes()
            st.success("Cliente eliminado")
    else:
        st.info("No hay clientes disponibles para modificar.")

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
    if not df_ventas.empty:
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

    st.subheader("📈 Gráfico de ventas por día")
    if not df_ventas.empty:
        ventas_por_dia = df_ventas.groupby("Fecha")["Total"].sum().reset_index()
        st.line_chart(ventas_por_dia.rename(columns={"Fecha": "index"}).set_index("index"))
        dia_mas = ventas_por_dia.loc[ventas_por_dia["Total"].idxmax()]
        dia_menos = ventas_por_dia.loc[ventas_por_dia["Total"].idxmin()]
        st.info(f"📈 Día con más ventas: {dia_mas['Fecha']} (${dia_mas['Total']:,.0f})")
        st.info(f"📉 Día con menos ventas: {dia_menos['Fecha']} (${dia_menos['Total']:,.0f})")

# === PREMIOS ===
elif menu == "Premios 🎁":
    st.title("🎁 Clientes que han alcanzado 30 almuerzos")
    premios = df_ventas.groupby("Cliente")["Cantidad"].sum().reset_index()
    premios_filtrados = premios[premios["Cantidad"] >= 30].sort_values(by="Cantidad", ascending=False)

    if premios_filtrados.empty:
        st.warning("Ningún cliente ha alcanzado los 30 almuerzos todavía.")
    else:
        st.dataframe(premios_filtrados.rename(columns={"Cantidad": "Almuerzos comprados"}))

