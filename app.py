import urllib.parse
import pandas as pd
import streamlit as st

# Configuración de la página web optimizada para dispositivos móviles
st.set_page_config(
    page_title="Directorio de Directores UGEL",
    page_icon="🏫",
    layout="centered",
)

# Estilo CSS inteligente: Cambia automáticamente entre el estilo institucional peruano (Tema Claro) y el Modo Oscuro
st.markdown(
    """
    <style>
    /* ---------------------------------------------------- */
    /* 1. TEMA CLARO: Estilo Institucional (Portal Estado Peruano) */
    /* ---------------------------------------------------- */
    @media (prefers-color-scheme: light) {
        .stApp {
            background-color: #f3f4f6 !important;
        }
        /* Barra superior institucional roja simulando el encabezado del estado */
        .header-gob {
            background-color: #DA1E28;
            padding: 12px;
            color: white;
            text-align: center;
            font-weight: bold;
            font-size: 14px;
            border-radius: 6px;
            margin-bottom: 20px;
        }
        /* Tarjetas estilo oficial en modo claro */
        .tarjeta-directorio {
            border: 1px solid #d1d5db !important;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 20px;
            background-color: #ffffff !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        .nombre-director {
            font-weight: bold;
            font-size: 16px;
            color: #111827 !important;
        }
        h2, p, label {
            color: #1f2937 !important;
        }
    }

    /* ---------------------------------------------------- */
    /* 2. TEMA OSCURO: Mantiene el diseño moderno y elegante */
    /* ---------------------------------------------------- */
    @media (prefers-color-scheme: dark) {
        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #090d16 100%);
            background-attachment: fixed;
        }
        .header-gob {
            background-color: #1e293b;
            border: 1px solid rgba(56, 189, 248, 0.2);
            padding: 12px;
            color: #38bdf8;
            text-align: center;
            font-weight: bold;
            font-size: 14px;
            border-radius: 6px;
            margin-bottom: 20px;
        }
        .tarjeta-directorio {
            border: 1px solid rgba(56, 189, 248, 0.2);
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 20px;
            background: rgba(30, 41, 59, 0.7);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        }
        .nombre-director {
            font-weight: bold;
            font-size: 16px;
            color: #f1f5f9 !important;
        }
    }

    /* Centrar perfectamente las flechitas del expander en ambos temas */
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
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Franja superior institucional estilo Gob.pe
st.markdown(
    '<div class="header-gob">PERÚ — Plataforma Digital del Estado Peruano | UGEL Directorio</div>',
    unsafe_allow_html=True,
)

# Sección de Membrete / Encabezado
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
    df = pd.read_excel(archivo_excel, sheet_name="PUBLICAS", dtype=str)
    df.columns = df.columns.str.strip()
    df = df.dropna(subset=["NOMBRE DIRECTOR", "IE"], how="all")
    return df


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


# Función auxiliar para buscar un valor buscando por palabras clave en las columnas
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
        f"<p style='font-size: 13px; text-align: center; margin-top: 5px;'><b>{total_resultados}</b> resultado(s) encontrado(s)</p>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    if total_resultados > 0:
        columnas_df = [c for c in df_filtrado.columns]

        for index, row in df_filtrado.
