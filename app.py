import urllib.parse
import pandas as pd
import streamlit as st

# Configuración de la página web optimizada para dispositivos móviles
st.set_page_config(
    page_title="Directorio de Directores UGEL",
    page_icon="🏫",
    layout="centered",
)

# Sección de Membrete / Encabezado institucional estilo UGEL
col_logo1, col_logo2, col_logo3 = st.columns([1, 1.5, 1])
with col_logo2:
    st.markdown(
        "<div style='text-align: center; font-size: 50px;'>🏛️</div>",
        unsafe_allow_html=True,
    )

st.markdown(
    "<h2 style='text-align: center; margin-bottom: 0px;'>UGEL - DIRECTORIO</h2>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; opacity: 0.7; font-size: 14px;'>Directorio"
    " de Directores - 2026</p>",
    unsafe_allow_html=True,
)
st.divider()


# Función para cargar únicamente la pestaña 'PUBLICAS'
@st.cache_data
def cargar_datos():
    archivo_excel = "BD - Directores.xlsx"
    # dtype=str asegura que Excel lea los códigos y números manteniendo los ceros a la izquierda
    df = pd.read_excel(archivo_excel, sheet_name="PUBLICAS", dtype=str)
    df.columns = df.columns.str.strip()
    df = df.dropna(subset=["NOMBRE DIRECTOR", "IE"], how="all")
    return df


# Función para limpiar texto conservando ceros a la izquierda y evitando eliminar .0 si es parte de texto real
def limpiar_texto(val):
    if pd.isna(val) or val == "nan" or val is None:
        return ""
    s = str(val).strip()
    # Si pandas leyó un número entero como flotante con .0 al final, lo removemos limpiamente
    if s.endswith(".0") and s[:-2].isdigit():
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
    busqueda = st.text_input(
        "",
        placeholder="🔍 Buscar por nombre, IE, DNI o palabra clave...",
        label_visibility="collapsed",
    )

    # Filtrado flexible por palabras
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

    # Contador limpio de resultados
    st.markdown(
        f"<p style='opacity: 0.7; font-size: 13px; text-align: center; margin-top: 5px;'><b>{total_resultados}</b> resultado(s) encontrado(s)</p>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    if total_resultados > 0:
        columnas_df = [c for c in df_filtrado.columns]

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

            with st.container():
                st.markdown(
                    f"""
                    <div style="
                        border: 1px solid rgba(150, 150, 150, 0.3);
                        border-radius: 10px;
                        padding: 15px;
                        margin-bottom: 20px;
                        background-color: rgba(100, 100, 100, 0.03);
                    ">
                        <div style="font-weight: bold; font-size: 16px; margin-bottom: 10px; border-bottom: 1px solid rgba(150, 150, 150, 0.2); padding-bottom: 8px;">
                            👤 {nombre_dir.upper()}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Estructura interna de 2 columnas dentro de cada tarjeta
                c_col1, c_col2 = st.columns(2)

                with c_col1:
                    st.markdown(f"**IE:** 🏫 {nombre_ie}")
                    if cod_modular:
                        # Se muestra el código tal cual (respetando ceros a la izquierda)
                        st.markdown(f"**Cód. Modular:** 🔢 {cod_modular}")
                    else:
                        st.markdown("**Cód. Modular:** 🔢 No registrado")

                with c_col2:
                    if celular:
                        num_limpio = "".join(filter(str.isdigit, celular))
                        num_whatsapp = (
                            f"51{num_limpio}"
                            if len(num_limpio) == 9
                            else num_limpio
                        )
                        link_wa = f"https://wa.me/{num_whatsapp}"
                        st.markdown(
                            f"**Celular:** 📞 [{celular}]({link_wa}) 🟢",
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown("**Celular:** 📞 No registrado")

                    if correo:
                        link_gmail = f"https://mail.google.com/mail/?view=cm&fs=1&to={urllib.parse.quote(correo)}"
                        st.markdown(
                            f"**Correo:** 📧 [{correo}]({link_gmail})",
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown("**Correo:** 📧 No registrado")

                # Expander con flechitas centradas llamativas y colores personalizados al desplegar
                with st.expander("▼  ▼  ▼"):
                    for col in columnas_df:
                        val = limpiar_texto(row[col])
                        col_upper = col.upper()
                        if not any(
                            k in col_upper
                            for k in [
                                "DIRECTOR",
                                "IE",
                                "CELULAR",
                                "MODULAR",
                                "CORREO",
                            ]
                        ):
                            if val != "" and val != "nan":
                                # Usamos HTML con colores diferenciados para el título y el valor después de los dos puntos
                                st.markdown(
                                    f"<div style='padding: 3px 0;'>"
                                    f"<span style='opacity: 0.7; font-weight: 500;'>{col}:</span> "
                                    f"<span style='font-weight: 600; color: #38bdf8;'>{val}</span>"
                                    f"</div>",
                                    unsafe_allow_html=True,
                                )

                st.markdown("---")
    else:
        st.warning(
            "No se encontraron coincidencias. Prueba buscando por una sola"
            " palabra o número."
        )

    # Botón de descarga al final de la página
    csv = df_filtrado.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Descargar resultados filtrados en CSV",
        data=csv,
        file_name="directorio_filtrado.csv",
        mime="text/csv",
        use_container_width=True,
    )

except Exception as e:
    st.error(f"Ocurrió un error al cargar los datos: {e}")
