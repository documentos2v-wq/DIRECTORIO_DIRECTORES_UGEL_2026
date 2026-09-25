import pandas as pd
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Directorio UGEL Otuzco 2026", page_icon="📚", layout="wide"
)

# Título principal
st.title("📌 Directorio de Servidores - UGEL Otuzco 2026")
st.markdown(
    "Herramienta automatizada para la consulta rápida del directorio institucional."
)


# Cargar los datos desde el archivo Excel
@st.cache_data
py
def cargar_datos():
  excel_path = "DIRECTORIO UGEL OTUZCO 2026.xlsx"
  # Leemos la cabecera real detectada en la fila 6 (índice 6)
  df_raw = pd.read_excel(excel_path, header=6)
  # Limpiamos columnas nulas o filas de secciones si las hay
  df_raw = df_raw.dropna(subset=["Nº", "NOMBRES Y APELLIDOS"], how="any")
  return df_raw


try:
  df = cargar_datos()

  # Barra lateral de filtros
  st.sidebar.header("🔍 Filtros de Búsqueda")
  busqueda = st.sidebar.text_input("Buscar por Nombre, DNI o Cargo:")

  # Filtro por Área si la columna existe
  if "AREA" in df.columns:
    areas = ["Todas"] + list(df["AREA"].dropna().unique())
    area_seleccionada = st.sidebar.selectbox("Filtrar por Área:", areas)
    if area_seleccionada != "Todas":
      df = df[df["AREA"] == area_seleccionada]

  # Aplicar búsqueda de texto
  if busqueda:
    # Convertimos todo a string para buscar sin errores
    df_filtered = df[
        df.astype(str)
        .apply(lambda x: x.str.contains(busqueda, case=False, na=False))
        .any(axis=1)
    ]
  else:
    df_filtered = df

  # Mostrar métricas rápidas
  st.metric(
      label="Total de Servidores Mostrados", value=len(df_filtered)
  )

  # Mostrar la tabla interactiva
  st.dataframe(df_filtered, use_container_width=True, hide_index=True)

  # Botón de descarga actualizado
  csv = df_filtered.to_csv(index=False).encode("utf-8")
  st.download_button(
      label="📥 Descargar Directorio Filtrado en CSV",
      data=csv,
      file_name="directorio_ugel_otuzco_filtrado.csv",
      mime="text/csv",
  )

except Exception as e:
  st.error(f"Error al cargar el archivo de Excel: {e}")