# Surtitienda Comunitaria - App Mejorada

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
        numero = st.text_input("Número")
        telefono = st.text_input("Teléfono de contacto")
        barrio = st.text_input("Barrio y/o dirección")
        comuna = st.text_input("Comuna")
        enviar = st.form_submit_button("Guardar cliente")

    if enviar:
        if nombre and telefono:
            if nombre.strip().lower() in df_clientes["NOMBRE Y APELLIDO COMPLETO"].str.strip().str.lower().values:
                st.error("❌ Ya existe un cliente con ese nombre.")
            elif numero.strip() in df_clientes["NUMERO"].astype(str).str.strip().values:
                st.error("❌ Ya existe un cliente con ese número.")
            elif telefono.strip() in df_clientes["TELEFONO CONTACTO"].astype(str).str.strip().values:
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
            st.error("Por favor completa los campos obligatorios.")

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
    pedido_borrar = st.number_input("# de pedido a eliminar", min_value=1, step=1)
    if st.button("Eliminar compra"):
        if pedido_borrar in df_ventas["# de pedido"].values:
            df_ventas = df_ventas[df_ventas["# de pedido"] != pedido_borrar]
            guardar_ventas()
            st.success("Compra eliminada correctamente.")
        else:
            st.error("No se encontró ese número de pedido.")

# === ACTUALIZAR / ELIMINAR CLIENTE ===
elif menu == "Actualizar / Eliminar Cliente":
    st.title("✏️ Actualizar o Eliminar Cliente")
    lista_clientes = df_clientes["NOMBRE Y APELLIDO COMPLETO"].tolist()
    seleccionado = st.selectbox("Selecciona un cliente", lista_clientes)
    idx = df_clientes[df_clientes["NOMBRE Y APELLIDO COMPLETO"] == seleccionado].index[0]

    with st.form("form_edit"):
        nombre = st.text_input("Nombre", df_clientes.loc[idx, "NOMBRE Y APELLIDO COMPLETO"])
        numero = st.text_input("Número", df_clientes.loc[idx, "NUMERO"])
        telefono = st.text_input("Teléfono", df_clientes.loc[idx, "TELEFONO CONTACTO"])
        barrio = st.text_input("Dirección", df_clientes.loc[idx, "BARRIO Y/O DIRRECCION"])
        comuna = st.text_input("Comuna", df_clientes.loc[idx, "COMUNA"])
        actualizar = st.form_submit_button("Actualizar")

    if actualizar:
        df_clientes.loc[idx, ["NOMBRE Y APELLIDO COMPLETO", "NUMERO", "TELEFONO CONTACTO", "BARRIO Y/O DIRRECCION", "COMUNA"]] = [nombre, numero, telefono, barrio, comuna]
        guardar_clientes()
        st.success("✅ Cliente actualizado")

    if st.button("Eliminar cliente"):
        df_clientes = df_clientes.drop(idx).reset_index(drop=True)
        guardar_clientes()
        st.success("🗑️ Cliente eliminado")

# === RESUMEN DE VENTAS ===
elif menu == "Resumen de Ventas":
    st.title("📊 Resumen Total de Ventas")
    if df_ventas.empty:
        st.info("No hay ventas registradas.")
    else:
        st.dataframe(df_ventas)
        st.metric("Total vendido", f"${df_ventas['Total'].sum():,.0f}")
        st.bar_chart(df_ventas.groupby("Vendedor")["Total"].sum())

# === PREMIOS ===
elif menu == "Premios 🎁":
    st.title("🎉 Clientes con Premios")
    df_premios = df_clientes[df_clientes["DIAS QUE VINO"] >= 30].copy()
    df_premios = df_premios.sort_values(by="DIAS QUE VINO", ascending=False)

    if df_premios.empty:
        st.info("Ningún cliente ha alcanzado los 30 almuerzos aún.")
    else:
        df_premios["Premios obtenidos"] = df_premios["DIAS QUE VINO"] // 30
        st.dataframe(df_premios[["NOMBRE Y APELLIDO COMPLETO", "DIAS QUE VINO", "Premios obtenidos"]])

