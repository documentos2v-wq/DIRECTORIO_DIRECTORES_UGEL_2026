import pandas as pd
import streamlit as st

# Configuración de la página web
st.set_page_config(
    page_title="Directorio de Directores UGEL 2026",
    page_icon="📊",
    layout="wide",
)

st.title("📌 Directorio de Directores - UGEL 2026")
st.markdown(
    "Utiliza el buscador general para filtrar la información de manera rápida por nombre, institución, código o cualquier otro dato del registro."
)


# Función para cargar los datos asegurando que se lean correctamente
@st.cache_data
def cargar_datos():
  # Lee el archivo Excel que ya se encuentra en tu repositorio
  archivo_excel = "BD - Directores.xlsx"
  df = pd.read_excel(archivo_excel)
  return df


# Cargar los datos
try:
  df = cargar_datos()

  # Barra de búsqueda automatizada global
  busqueda = st.text_input(
      "🔍 Escribe para buscar (nombre, institución, DNI, etc.):"
  )

  # Filtrar el DataFrame si el usuario escribe algo
  if busqueda:
    # Convierte todo el DataFrame a texto y busca coincidencias sin distinguir mayúsculas/minúsculas
    mask = (
        df.astype(str)
        .apply(lambda x: x.str.contains(busqueda, case=False, na=False))
        .any(axis=1)
    )
    df_filtrado = df[mask]
  else:
    df_filtrado = df

  # Mostrar métricas rápidas de los resultados
  st.info(
      f"Mostrando {len(df_filtrado)} de {len(df)} registros totales en el"
      " sistema."
  )

  # Mostrar la tabla interactiva
  st.dataframe(df_filtrado, use_container_width=True)

  # Opción opcional para descargar los resultados filtrados en CSV
  csv = df_filtrado.to_csv(index=False).encode("utf-8")
  st.download_button(
      label="📥 Descargar resultados filtrados en CSV",
      data=csv,
      file_name="directores_filtrados.csv",
      mime="text/csv",
  )

except Exception as e:
  st.error(
      f"Ocurrió un error al cargar el archivo 'BD - Directores.xlsx': {e}"
  )
  st.warning(
      "Asegúrate de que el archivo Excel se encuentre en la misma carpeta que"
      " 'app.py' en tu repositorio."
  )
