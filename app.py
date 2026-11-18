import urllib.parse
import pandas as pd
import streamlit as st

# Configuración de la página web optimizada para dispositivos móviles y PC
st.set_page_config(
    page_title="UGELO - Buscador",
    page_icon="🏫",
    layout="centered",
)

# Estilo CSS avanzado: Responsive total para PC y Celulares
st.markdown(
    """
    <style>
    .stApp {
        background-color: #ffffff;
    }
    
    @media (prefers-color-scheme: dark) {
        .stApp {
            background-color: #0f172a !important;
        }
        h2, p, label {
            color: #f8fafc !important;
        }
    }

    /* Logotipo estilo Google (UGELO en mayúsculas forzadas y responsivo) */
    .google-logo {
        font-family: Arial, sans-serif;
        font-size: clamp(45px, 10vw, 68px);
        font-weight: bold;
        text-align: center;
        margin-top: 3rem;
        margin-bottom: 1.5rem;
        letter-spacing: -2px;
        text-transform: uppercase !important;
    }
    .g-u { color: #4285F4; }
    .g-g { color: #EA4335; }
    .g-e { color: #FBBC05; }
    .g-l { color: #4285F4; }
    .g-o { color: #34A853; }

    /* Tarjetas de directores adaptables a móviles y PC */
    .tarjeta-directorio {
        border: 1px solid #dfe1e5 !important;
        border-left: 5px solid #4285F4 !important;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 15px;
        background-color: #ffffff !important;
        box-shadow: 0 1px 6px rgba(32, 33, 36, 0.08);
    }
    
    @media (prefers-color-scheme: dark) {
        .tarjeta-directorio {
            border: 1px solid rgba(56, 189, 248, 0.2);
            border-left: 5px solid #4285F4 !important;
            background: rgba(30, 41, 59, 0.85) !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        }
    }

    .nombre-director {
        font-weight: 700;
        font-size: 16px;
        color: #202124;
    }
    @media (prefers-color-scheme: dark) {
        .nombre-director {
            color: #f8fafc !important;
        }
    }

    /* Estilo para el expander de detalles */
    [data-testid="stExpander"] details summary {
        display: flex;
        justify-content: center;
        align-items: center;
    }
    [data-testid="stExpander"] details summary p {
        text-align: center !important;
        width: 100% !important;
        font-weight: bold;
        letter-spacing: 6px;
        font-size: 0px !important;
    }
    [data-testid="stExpander"] details:not([open]) summary p::after {
        content: " ▼ ▼ ▼";
        font-size: 14px !important;
        color: #5f6368;
    }
    [data-testid="stExpander"] details[open] summary p::after {
        content: " ▲ ▲ ▲";
        font-size: 14px !important;
        color: #5f6368;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Logo central estilo Google forzado en mayúsculas: U-G-E-L-O
st.markdown(
    """
    <div class="google-logo">
        <span class="g-u">U</span><span class="g-g">G</span><span class="g-e">E</span><span class="g-l">L</span><span class="g-o">O</span>
    </div>
    """,
    unsafe_allow_html=True,
)


# Función para limpiar texto y asegurar ceros iniciales
def limpiar_texto(val, nombre_col=""):
    if pd.isna(val) or val == "nan" or val is None:
        return ""
    s = str(val).strip()
    if s.endswith(".0") and s[:-2].isdigit():
        s = s[:-2]

    col_up = str(nombre_col).upper()
    if "MODULAR" in col_up and s.isdigit():
        if len(s) < 7:
            s = s.zfill(7)
    elif "DNI" in col_up and s.isdigit():
        if len(s) < 8:
            s = s.zfill(8)

    return s


# Función optimizada para cargar datos y precalcular columna de texto de búsqueda
@st.cache_data
def cargar_datos():
    archivo_excel = "BD - Directores.xlsx"
    df = pd.read_excel(archivo_excel, sheet_name="PUBLICAS", dtype=str)
    df.columns = df.columns.str.strip().str.upper()

    col_dir = next((c for c in df.columns if "DIRECTOR" in c), None)
    col_ie = next((c for c in df.columns if "IE" in c or "INSTITUCION" in c), None)

    if col_dir and col_ie:
        df = df.dropna(subset=[col_dir, col_ie], how="all")

    df = df.fillna("")

    # Columna oculta para búsqueda ultra rápida y sin tildes
    df["_SEARCH_TEXT"] = (
        df.astype(str)
        .apply(lambda x: " ".join(x), axis=1)
        .str.lower()
        .str.normalize("NFKD")
        .str.encode("ascii", errors="ignore")
        .str.decode("utf-8")
    )

    return df


# Función auxiliar para buscar campos rápidamente
def obtener_campo(row, keywords):
    for col in row.index:
        col_up = str(col).upper()
        if any(k in col_up for k in keywords):
            val = limpiar_texto(row[col], col)
            if val != "" and val != "nan":
                return val
    return ""


try:
    df = cargar_datos()

    # Buscador centralizado adaptable a PC y Celular
    _, col_buscador, _ = st.columns([0.1, 2.8, 0.1])

    with col_buscador:
        busqueda = st.text_input(
            "",
            placeholder="🔍 Busca por IE, DNI, Apellido, Código Modular...",
            label_visibility="collapsed",
        )

    # Solo realizamos y mostramos resultados si el usuario ha escrito algo
    if busqueda and busqueda.strip() != "":
        palabras = busqueda.strip().split()
        mask = pd.Series(True, index=df.index)

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

                sub_mask = df["_SEARCH_TEXT"].str.contains(p_limpia, na=False)
                if p_alternativa and p_alternativa != p_limpia:
                    sub_mask = sub_mask | df["_SEARCH_TEXT"].str.contains(
                        p_alternativa, na=False
                    )

                mask = mask & sub_mask

        df_filtrado = df[mask]
        total_resultados = len(df_filtrado)

        # Contador limpio de resultados
        st.markdown(
            f"<p style='font-size: 13px; text-align: center; color: #5f6368; margin-top: 15px;'>Cerca de <b>{total_resultados}</b> resultado(s) encontrado(s)</p>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<hr style='border: 0; border-top: 1px solid #dfe1e5;'>",
            unsafe_allow_html=True,
        )

        if total_resultados > 0:
            columnas_df = [c for c in df_filtrado.columns if c != "_SEARCH_TEXT"]

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
                        <div class="tarjeta-directorio">
                            <div class="nombre-director">
                                👤 {nombre_dir.upper()}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    c_col1, c_col2 = st.columns([1, 1])

                    with c_col1:
                        st.markdown(f"**IE:** 🏫 {nombre_ie}")
                        if cod_modular:
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

                    with st.expander("detalles"):
                        for col in columnas_df:
                            val = limpiar_texto(row[col], col)
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
                                    st.markdown(
                                        f"<div style='padding: 3px 0;'>"
                                        f"<span style='font-weight: 500;'>{col}:</span> "
                                        f"<span style='font-weight: 600; color: #1a0dab;'>{val}</span>"
                                        f"</div>",
                                        unsafe_allow_html=True,
                                    )

                    st.markdown(
                        "<hr style='border: 0; border-top: 1px solid #f1f3f4;'>",
                        unsafe_allow_html=True,
                    )
        else:
            st.warning(
                "No se encontraron coincidencias. Prueba buscando por una sola"
                " palabra o número (ej: 80910)."
            )

        # Botón de descarga al final de la página (solo visible al buscar)
        df_export = df_filtrado.drop(columns=["_SEARCH_TEXT"], errors="ignore")
        csv = df_export.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Descargar resultados filtrados en CSV",
            data=csv,
            file_name="directorio_ugelo_filtrado.csv",
            mime="text/csv",
            use_container_width=True,
        )

except Exception as e:
    st.error(f"Ocurrió un error al cargar los datos: {e}")
