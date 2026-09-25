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


# Función para cargar los datos
@st.cache_data
def cargar_datos():
  archivo_excel = "BD - Directores.xlsx"
  df = pd.read_excel(archivo_excel)
  # Limpiar espacios en blanco en los nombres de las columnas
  df.columns = df.columns.str.strip()
  return df


try:
  df = cargar_datos()

  # Buscador general inteligente
  st.markdown("### 🔍 Buscador General")
  busqueda = st.text_input(
      "",
      placeholder="Ej: Castro Rodriguez, Juan, Primaria...",
      label_visibility="collapsed",
  )

  # Filtrado avanzado por palabras independientes
  if busqueda:
    # Separamos lo que escribe el usuario por espacios (ej: ["CASTRO", "RODRIGUEZ"])
    palabras = busqueda.strip().split()

    # Unimos todas las columnas en un solo texto por fila para buscar en todo el registro
    df_texto = (
        df.astype(str)
        .apply(lambda x: " ".join(x), axis=1)
        .str.lower()
        .str.normalize("NFKD")
        .str.encode("ascii", errors="ignore")
        .str.decode("utf-8")
    )

    # Creamos una máscara que verifique si CADA palabra ingresada está presente en el registro
    mask = pd.Series(True, index=df.index)
    for palabra in palabras:
      p_limpia = (
          palabra.lower()
          .encode("ascii", errors="ignore")
          .decode("utf-8")
          .strip()
      )
      if p_limpia:
        mask = mask & df_texto.str.contains(p_limpia, na=False)

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
    columnas = df_filtrado.columns.tolist()

    for index, row in df_filtrado.iterrows():
      titulo = str(row.get(columnas[1], row.get(columnas[0], "Registro")))
      subtitulo = str(row.get(columnas[2], "")) if len(columnas) > 2 else ""

      with st.expander(f"📌 {titulo}"):
        if subtitulo:
          st.markdown(f"**Detalle principal:** {subtitulo}")

        for col in columnas:
          val = row[col]
          if pd.notna(val) and str(val).strip() != "":
            st.text(f"{col}: {val}")
  else:
    st.warning(
        "No se encontraron coincidencias con los términos ingresados. Prueba"
        " escribiendo solo una parte del nombre o apellido."
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
