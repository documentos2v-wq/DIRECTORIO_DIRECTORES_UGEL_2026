import urllib.parse
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


# Función para cargar únicamente la pestaña 'PUBLICAS'
@st.cache_data
def cargar_datos():
  archivo_excel = "BD - Directores.xlsx"
  df = pd.read_excel(archivo_excel, sheet_name="PUBLICAS")
  df.columns = df.columns.str.strip()
  df = df.dropna(subset=["NOMBRE DIRECTOR", "IE"], how="all")
  df["CATEGORIA_HOJA"] = "PUBLICAS"
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

  # Sección superior de herramientas de correo masivo vía Gmail
  with st.expander(
      "📧 Herramientas de Correo Masivo (Enviar a todos los filtrados)"
  ):
    st.markdown(
        "Puedes redactar un correo y abrirlo directamente en **Gmail** con"
        " todos los directores filtrados."
    )
    asunto_correo = st.text_input("Asunto del correo:", value="Comunicado UGEL")
    cuerpo_correo = st.text_area(
        "Mensaje del correo:",
        value="Estimados directores,\n\nPor medio del presente...",
    )

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
        p_alternativa = p_limpia.lstrip("0") if p_limpia.isdigit() else p_limpia

        mask = mask | df_texto.str.contains(p_limpia, na=False)
        if p_alternativa and p_alternativa != p_limpia:
          mask = mask | df_texto.str.contains(p_alternativa, na=False)

    df_filtrado = df[mask]
  else:
    df_filtrado = df

  total_resultados = len(df_filtrado)

  # Extraer todos los correos válidos de los resultados actuales filtrados
  correos_filtrados = []
  for _, row in df_filtrado.iterrows():
    c = obtener_campo(row, ["CORREO", "EMAIL"])
    if c and "@" in c:
      correos_filtrados.append(c)

  # Botón dinámico para abrir Gmail con los correos en BCC
  if correos_filtrados:
    lista_bcc = ",".join(correos_filtrados)
    # Enlace directo a la interfaz web de Gmail con asunto, cuerpo y bcc prellenados
    gmail_link = f"https://mail.google.com/mail/?view=cm&fs=1&bcc={urllib.parse.quote(lista_bcc)}&su={urllib.parse.quote(asunto_correo)}&body={urllib.parse.quote(cuerpo_correo)}"

    st.markdown(
        f'<a href="{gmail_link}" target="_blank" style="display: block; text-align: center; background-color: #EA4335; color: white; padding: 12px; border-radius: 5px; text-decoration: none; font-weight: bold; margin-bottom: 10px;">✉️ Abrir en Gmail y enviar a los {len(correos_filtrados)} directores</a>',
        unsafe_allow_html=True,
    )

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
        nombre_dir = obtener_campo(row, ["DIRECTOR", "NOMBRES Y APELLIDOS"])
        nombre_ie = obtener_campo(row, ["IE", "INSTITUCION"])
        celular = obtener_campo(row, ["CELULAR", "TELEFONO", "MOVIL"])
        cod_modular = obtener_campo(row, ["MODULAR", "CODIGO MODULAR"])

        if not nombre_dir:
          nombre_dir = "Sin nombre registrado"
        if not nombre_ie:
          nombre_ie = "IE sin nombre"

        # Título principal de la tarjeta
        if celular:
          titulo_tarjeta = (
              f"🏫 {nombre_ie} — 👤 {nombre_dir} — 📞 {celular}"
          )
        else:
          titulo_tarjeta = f"🏫 {nombre_ie} — 👤 {nombre_dir} — 📞 (Sin celular)"

        with st.expander(titulo_tarjeta):
          st.caption(f"📁 Sección: {row.get('CATEGORIA_HOJA', '')}")

          st.markdown(f"**IE:** 🏫 {nombre_ie}")
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
          else:
            st.markdown("**Celular:** 📞 No registrado")

          if cod_modular:
            st.markdown(f"**Código Modular:** 🔢 {cod_modular}")
          else:
            st.markdown("**Código Modular:** 🔢 No registrado")

          st.divider()
          st.markdown("**Otros detalles del registro:**")

          for col in columnas:
            val = limpiar_texto(row[col])
            col_upper = col.upper()
            if not any(
                k in col_upper
                for k in ["DIRECTOR", "IE", "CELULAR", "MODULAR"]
            ):
              if val != "" and val != "nan":
                if "CORREO" in col_upper:
                  correo_val = val
                  # Enlace directo para redactar correo individual en Gmail web
                  link_gmail_ind = f"https://mail.google.com/mail/?view=cm&fs=1&to={urllib.parse.quote(correo_val)}"
                  st.markdown(
                      f"{col}: 📧 [{correo_val}]({link_gmail_ind}) *(Abrir en"
                      " Gmail)*",
                      unsafe_allow_html=True,
                  )
                else:
                  st.text(f"{col}: {val}")
  else:
    st.warning(
        "No se encontraron coincidencias. Prueba buscando por una sola palabra"
        " o número."
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
