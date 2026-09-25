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
    " palabra clave de forma rápida y ordenada.</p>",
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
    temp_df.columns = temp_df.columns.str.strip()
    temp_df["CATEGORIA_HOJA"] = sheet
    dfs.append(temp_df)

  df_total = pd.concat(dfs, ignore_index=True, sort=False)
  return df_total


# Función para eliminar el .0 de cualquier número o código
def limpiar_texto(val):
  if pd.isna(val):
    return ""
  s = str(val).strip()
  if s.endswith(".0"):
    s = s[:-2]
  return s


try:
  df = cargar_datos()

  # Buscador general inteligente y flexible
  st.markdown("### 🔍 Buscador General")
  busqueda = st.text_input(
      "",
      placeholder="Ej: Castro, Rodriguez, Juan...",
      label_visibility="collapsed",
  )

  # Filtrado flexible por palabras (Lógica OR)
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
        mask = mask | df_texto.str.contains(p_limpia, na=False)

    df_filtrado = df[mask]
  else:
    df_filtrado = df

  total_resultados = len(df_filtrado)

  # Contador de resultados
  st.markdown(
      f"<p style='color: #6B7280; font-size: 14px;'>Se encontraron"
      f" <b>{total_resultados}</b> registros.</p>",
      unsafe_allow_html=True,
  )
  st.divider()

  # Contenedor con barra de desplazamiento vertical de altura fija
  if total_resultados > 0:
    columnas = [c for c in df_filtrado.columns if c != "CATEGORIA_HOJA"]

    with st.container(height=480):
      for index, row in df_filtrado.iterrows():
        # Extraer campos clave de forma segura
        nombre_dir = limpiar_texto(row.get("NOMBRE DIRECTOR", ""))
        nombre_ie = limpiar_texto(row.get("IE", ""))
        celular = limpiar_texto(row.get("CELULAR", ""))
        cod_modular = limpiar_texto(row.get("CODIGO MODULAR", ""))

        # Definir el título visible de la tarjeta con la IE y el Director
        titulo_tarjeta = f"🏫 {nombre_ie} — 👤 {nombre_dir}"

        with st.expander(titulo_tarjeta):
          st.caption(f"📁 Sección: {row.get('CATEGORIA_HOJA', '')}")

          # Mostrar explícitamente los datos principales solicitados arriba
          if nombre_ie:
            st.markdown(f"**IE:** 🏫 {nombre_ie}")
          if nombre_dir:
            st.markdown(f"**Nombre Director:** 👤 {nombre_dir}")

          if celular:
            num_limpio = "".join(filter(str.isdigit, celular))
            num_whatsapp = (
                f"51{num_limpio}" if len(num_limpio) == 9 else num_limpio
            )
            link_wa = f"https://wa.me/{num_whatsapp}"
            st.markdown(
                f"**Celular:** 📞 [{celular}]({link_wa}) 🟢 *(Clic para"
                " WhatsApp)*",
                unsafe_allow_html=True,
            )

          if cod_modular:
            st.markdown(f"**Código Modular:** 🔢 {cod_modular}")

          st.divider()
          st.markdown("**Otros detalles del registro:**")

          # Mostrar el resto de campos que no sean los principales ya mostrados
          principales = [
              "NOMBRE DIRECTOR",
              "IE",
              "CELULAR",
              "CODIGO MODULAR",
              "DJ CORREO",
          ]
          for col in columnas:
            if col not in principales:
              val = limpiar_texto(row[col])
              if val != "" and val != "nan":
                col_upper = col.upper()
                if "CORREO" in col_upper:
                  st.text(f"{col}: 📧 {val}")
                else:
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
      mime="text/css",
      use_container_width=True,
  )

except Exception as e:
  st.error(f"Ocurrió un error al cargar los datos: {e}")
