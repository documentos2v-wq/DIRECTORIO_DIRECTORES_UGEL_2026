import pandas as pd
import streamlit as st

# Configuración de la página web optimizada para dispositivos móviles
st.set_page_config(
    page_title="Directorio de Directores UGEL 2026",
    page_icon="🏫",
    layout="centered",
)

st.markdown(
    "<h1 style='text-align: center; color: #1E3A8A;'>Directory de"
    " Directores</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; color: #4B5563;'>Busca de forma rápida y"
    " ordenada la información de las instituciones educativas.</p>",
    unsafe_allow_html=True,
)


# Función para cargar los datos
@st.cache_data
def cargar_datos():
  archivo_excel = "BD - Directores.xlsx"
  df = pd.read_excel(archivo_excel)
  # Limpiar espacios en blanco en los nombres de las columnas por seguridad
  df.columns = df.columns.str.strip()
  return df


try:
  df = cargar_datos()

  # Buscador general automatizado
  st.markdown("### 🔍 Buscador General")
  busqueda = st.text_input(
      "",
      placeholder="Escribe nombre, institución, DNI o código...",
      label_visibility="collapsed",
  )

  # Filtrado global
  if busqueda:
    mask = (
        df.astype(str)
        .apply(lambda x: x.str.contains(busqueda, case=False, na=False))
        .any(axis=1)
    )
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
    # Identificar nombres lógicos de columnas si existen, o usar las primeras disponibles
    columnas = df_filtrado.columns.tolist()

    for index, row in df_filtrado.iterrows():
      # Tomamos el primer valor como título principal (ej: Nombre o Institución) y el segundo como subtítulo
      titulo = str(
          row.get(columnas[1], row.get(columnas[0], "Registro"))
      )  # Ajusta según tus columnas
      subtitulo = str(row.get(columnas[2], "")) if len(columnas) > 2 else ""

      # Creamos una tarjeta expandible para cada registro
      with st.expander(f"📌 {titulo}"):
        if subtitulo:
          st.markdown(f"**Detalle principal:** {subtitulo}")

        # Mostrar todos los campos restantes de manera ordenada en lista
        for col in columnas:
          val = row[col]
          if pd.notna(val) and str(val).strip() != "":
            st.text(f"{col}: {val}")
  else:
    st.warning(
        "No se encontraron coincidencias con los datos ingresados. Intente"
        " con otro término."
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
