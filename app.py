import pandas as pd
import streamlit as st

# Configuración de la página web optimizada para dispositivos móviles
st.set_page_config(
    page_title="Directorio de Directores UGEL 2026",
    page_icon="🏫",
    layout="centered",
)

st.markdown(
    "<h1 style='text-align: center; color: #1E3A8A;'>Directorio de"
    " Directores</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; color: #4B5563;'>Busca por cualquier"
    " palabra clave (nombre, apellido, institución, etc.).</p>",
    unsafe_allow_html=True,
)


# Función para cargar y unificar todas las hojas del Excel
@st.cache_data
def cargar_datos():
  archivo_excel = "BD - Directores.xlsx"
  xls = pd.ExcelFile(archivo_excel)

  dfs = []
  for sheet in xls.sheet_names:
    temp_df = pd.read_excel(xls, sheet_name=sheet)
    # Limpiar espacios en los nombres de columnas
    temp_df.columns = temp_df.columns.str.strip()
    # Agregar una columna para saber de qué categoría/pestaña proviene si es útil
    temp_df["CATEGORIA_HOJA"] = sheet
    dfs.append(temp_df)

  # Unir todas las hojas en una sola tabla general
  df_total = pd.concat(dfs, ignore_index=True, sort=False)
  return df_total


try:
  df = cargar_datos()

  # Buscador general inteligente y flexible
  st.markdown("### 🔍 Buscador General")
  busqueda = st.text_input(
      "",
      placeholder="Ej: Castro, Rodriguez, Juan, Primaria...",
      label_visibility="collapsed",
  )

  # Filtrado flexible por palabras (Lógica OR: encuentra registros que coincidan con CUALQUIER palabra)
  if busqueda:
    palabras = busqueda.strip().split()

    # Rellenar nulos y convertir todo el DataFrame a texto plano (sin tildes, minúsculas)
    df_texto = (
        df.fillna("")
        .astype(str)
        .apply(lambda x: " ".join(x), axis=1)
        .str.lower()
        .str.normalize("NFKD")
        .str.encode("ascii", errors="ignore")
        .str.decode("utf-8")
    )

    # Creamos una máscara con lógica OR (|): basta que una palabra coincida
    mask = pd.Series(False, index=df.index)
    for palabra in palabras:
      p_limpia = (
          palabra.lower()
          .encode("ascii", errors="ignore")
          .decode("utf-8")
          .strip()
      )
      if p_limpia:
        mask = mask | df_texto.str.contains(p_limpia, na=False)

    df_filtrado = df[mask]
  else:
    df_filtrado = df

  # Contador de resultados
  st.markdown(
      f"<p style='color: #6B7280; font-size: 14px;'>Se encontraron"
      f" <b>{len(df_filtrado)}</b> registros.</p>",
      unsafe_allow_html=True,
  )
  st.divider()

  # Mostrar resultados en formato de tarjetas limpias (ideal para celulares)
  if len(df_filtrado) > 0:
    columnas = [c for c in df_filtrado.columns if c != "CATEGORIA_HOJA"]

    for index, row in df_filtrado.iterrows():
      # Intentar extraer un título claro (nombre o institución)
      titulo = str(
          row.get(
              "NOMBRE DIRECTOR",
              row.get(columnas[1], row.get(columnas[0], "Registro")),
          )
      )
      subt_col = (
          "IE"
          if "IE" in df_filtrado.columns
          else (columnas[2] if len(columnas) > 2 else "")
      )
      subtitulo = str(row.get(subt_col, ""))

      with st.expander(f"📌 {titulo}"):
        if subtitulo and subtitulo != "nan":
          st.markdown(f"**Institución / Detalle:** {subtitulo}")

        # Mostrar sección de la hoja de origen
        st.caption(f"📁 Sección: {row.get('CATEGORIA_HOJA', '')}")

        # Mostrar campos restantes
        for col in columnas:
          val = row[col]
          if pd.notna(val) and str(val).strip() != "" and str(val) != "nan":
            st.text(f"{col}: {val}")
  else:
    st.warning(
        "No se encontraron coincidencias. Prueba buscando por una sola palabra"
        " (por ejemplo: 'Castro')."
    )

  # Botón de descarga al final de la página
  st.divider()
  csv = df_filtrado.to_csv(index=False).encode("utf-8")
  st.download_button(
      label="📥 Descargar resultados en CSV",
      data=csv,
      file_name="directores_filtrados.csv",
      mime="text/csv",
      use_container_width=True,
  )

except Exception as e:
  st.error(f"Ocurrió un error al cargar los datos: {e}")
