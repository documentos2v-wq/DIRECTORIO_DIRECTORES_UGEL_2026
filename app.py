import urllib.parse
import pandas as pd
import streamlit as st

# Configuración de la página web optimizada para dispositivos móviles
st.set_page_config(
    page_title="Directorio de Directores UGEL 2026",
    page_icon="🏫",
    layout="centered",
)

# Títulos adaptativos al tema del navegador (sin colores forzados que desentonen)
st.markdown(
    "<h1 style='text-align: center;'>Directorio de Directores</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; opacity: 0.8;'>Busca por cualquier palabra"
    " clave de forma rápida y ordenada.</p>",
    unsafe_allow_html=True,
)


# Función para cargar únicamente la pestaña 'PUBLICAS'
@st.cache_data
def cargar_datos():
    archivo_excel = "BD - Directores.xlsx"
    df = pd.read_excel(archivo_excel, sheet_name="PUBLICAS")
    df.columns = df.columns.str.strip()
    df = df.dropna(subset=["NOMBRE DIRECTOR", "IE"], how="all")
    return df


# Función para eliminar el .0 de cualquier número o código
def limpiar_texto(val):
    if pd.isna(val):
        return ""
    s = str(val).strip()
    if s.endswith(".0"):
        s = s[:-2]
    return s


# Función auxiliar para buscar un valor buscando por palabras clave en las columnas
def obtener_campo(row, keywords):
    for col in row.index:
        col_up = str(col).upper()
        if any(k in col_up for k in keywords):
            val = limpiar_texto(row[col])
            if val != "" and val != "nan":
                return val
    return ""


try:
    df = cargar_datos()

    # Buscador general inteligente y flexible
    st.markdown("### 🔍 Buscador General")
    busqueda = st.text_input(
        "",
        placeholder="Ej: Castro, 267385, Juan, Primaria...",
        label_visibility="collapsed",
    )

    # Filtrado flexible por palabras (Lógica OR robusta frente a ceros iniciales y números)
    if busqueda:
        palabras = busqueda.strip().split()

        df_texto = (
            df.fillna("")
            .astype(str)
            .apply(lambda x: " ".join(x), axis=1)
            .str.lower()
            .str.normalize("NFKD")
            .str.encode("ascii", errors="ignore")
            .str.decode("utf-8")
        )

        mask = pd.Series(False, index=df.index)
        for palabra in palabras:
            p_limpia = (
                palabra.lower()
                .encode("ascii", errors="ignore")
                .decode("utf-8")
                .strip()
            )
            if p_limpia:
                p_alternativa = (
                    p_limpia.lstrip("0") if p_limpia.isdigit() else p_limpia
                )

                mask = mask | df_texto.str.contains(p_limpia, na=False)
                if p_alternativa and p_alternativa != p_limpia:
                    mask = mask | df_texto.str.contains(
                        p_alternativa, na=False
                    )

        df_filtrado = df[mask]
    else:
        df_filtrado = df

    total_resultados = len(df_filtrado)

    # Contador de resultados con opacidad adaptativa
    st.markdown(
        f"<p style='opacity: 0.7; font-size: 14px;'>Se encontraron"
        f" <b>{total_resultados}</b> registros.</p>",
        unsafe_allow_html=True,
    )
    st.divider()

    # Mostrar resultados de forma fluida, 100% responsiva para cualquier pantalla
    if total_resultados > 0:
        columnas = [c for c in df_filtrado.columns]

        for index, row in df_filtrado.iterrows():
            nombre_dir = obtener_campo(
                row, ["DIRECTOR", "NOMBRES Y APELLIDOS"]
            )
            nombre_ie = obtener_campo(row, ["IE", "INSTITUCION"])
            celular = obtener_campo(row, ["CELULAR", "TELEFONO", "MOVIL"])
            cod_modular = obtener_campo(row, ["MODULAR", "CODIGO MODULAR"])
            correo = obtener_campo(row, ["CORREO", "EMAIL"])

            if not nombre_dir:
                nombre_dir = "Sin nombre registrado"
            if not nombre_ie:
                nombre_ie = "IE sin nombre"

            # Título principal adaptativo para el expander
            if celular:
                titulo_tarjeta = (
                    f"🏫 {nombre_ie} — 👤 {nombre_dir} — 📞 {celular}"
                )
            else:
                titulo_tarjeta = (
                    f"🏫 {nombre_ie} — 👤 {nombre_dir} — 📞 (Sin celular)"
                )

            with st.expander(titulo_tarjeta):
                st.markdown(f"**IE:** 🏫 {nombre_ie}")
                st.markdown(f"**Nombre Director:** 👤 {nombre_dir}")

                if celular:
                    num_limpio = "".join(filter(str.isdigit, celular))
                    num_whatsapp = (
                        f"51{num_limpio}"
                        if len(num_limpio) == 9
                        else num_limpio
                    )
                    link_wa = f"https://wa.me/{num_whatsapp}"
                    st.markdown(
                        f"**Celular:** 📞 [{celular}]({link_wa}) 🟢 *(Clic para"
                        " WhatsApp)*",
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown("**Celular:** 📞 No registrado")

                if cod_modular:
                    st.markdown(f"**Código Modular:** 🔢 {cod_modular}")
                else:
                    st.markdown("**Código Modular:** 🔢 No registrado")

                # Correo principal y botón adaptable para móviles y PC
                if correo:
                    link_gmail_ind = f"https://mail.google.com/mail/?view=cm&fs=1&to={urllib.parse.quote(correo)}"
                    
                    # Usamos columnas adaptativas (se apilan automáticamente en pantallas muy chicas)
                    col_mail1, col_mail2 = st.columns([2.5, 1])
                    with col_mail1:
                        st.markdown(
                            f"**Correo:** 📧 [{correo}]({link_gmail_ind})"
                            " *(Abrir en Gmail)*",
                            unsafe_allow_html=True,
                        )
                    with col_mail2:
                        if st
