import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Archivo local donde se guardará la base de datos
DB_FILE = "asistencia_iglesia.csv"

# Configuración de interfaz móvil
st.set_page_config(page_title="Control Asistencia", page_icon="⛪", layout="centered")

# Función para inicializar o cargar los datos
def cargar_datos():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    else:
        # Estructura base si el archivo no existe
        return pd.DataFrame(columns=["Nombre Completo", "Sexo", "Contacto", "Sector"])

def guardar_datos(df):
    df.to_csv(DB_FILE, index=False)

# Cargar datos en la sesión actual
if 'df' not in st.session_state:
    st.session_state.df = cargar_datos()

st.title("⛪ Control de Asistencia")

# Navegación con pestañas
tab1, tab2, tab3 = st.tabs(["📋 Lista", "👥 Hermanos", "⚙️ Datos"])

# --- 1. Pestaña de Asistencia ---
with tab1:
    st.subheader("Tomar Asistencia")
    
    # Selector de fecha y nombre de la actividad
    col1, col2 = st.columns(2)
    with col1:
        fecha_seleccionada = st.date_input("Fecha de la actividad", datetime.now())
    with col2:
        nombre_actividad = st.text_input("Nombre de la actividad", "Culto General")
        
    # Construimos el nombre de la columna uniendo fecha y actividad
    columna_asistencia = f"{fecha_seleccionada} - {nombre_actividad.strip()}"
    
    df = st.session_state.df

    if not df.empty:
        st.write(f"**Registrando asistencia para:** {columna_asistencia}")
        
        # Si no existe la columna de esta actividad, la crea con valor False
        if columna_asistencia not in df.columns:
            df[columna_asistencia] = False

        # Filtramos para mostrar solo Nombre y la casilla de la actividad
        columnas_mostrar = ["Nombre Completo", columna_asistencia]

        # Editor interactivo para marcar los checks
        df_editado = st.data_editor(
            df[columnas_mostrar],
            hide_index=True,
            use_container_width=True,
            disabled=["Nombre Completo"] # Solo se edita el check, no el nombre
        )

        if st.button("💾 Guardar Asistencia"):
            st.session_state.df[columna_asistencia] = df_editado[columna_asistencia]
            guardar_datos(st.session_state.df)
            st.success(f"¡Asistencia de '{columna_asistencia}' guardada correctamente!")
    else:
        st.info("No hay hermanos registrados. Ve a la pestaña 'Hermanos'.")

# --- 2. Pestaña de Gestión de Creyentes ---
with tab2:
    st.subheader("Agregar Nuevo Hermano")
    with st.form("nuevo_hermano", clear_on_submit=True):
        nombre = st.text_input("Nombre Completo")
        sexo = st.selectbox("Sexo", ["M", "F"])
        contacto = st.text_input("Contacto (Teléfono)")
        sector = st.text_input("Sector / Barrio")
        submit = st.form_submit_button("➕ Agregar")

        if submit and nombre:
            nuevo_registro = pd.DataFrame([{
                "Nombre Completo": nombre.upper(),
                "Sexo": sexo,
                "Contacto": str(contacto),
                "Sector": sector.upper()
            }])
            st.session_state.df = pd.concat([st.session_state.df, nuevo_registro], ignore_index=True)
            guardar_datos(st.session_state.df)
            st.success(f"{nombre} agregado con éxito.")
            st.rerun()

    st.subheader("Directorio (Ver y Editar)")
    if not st.session_state.df.empty:
        cols_directorio = ["Nombre Completo", "Sexo", "Contacto", "Sector"]
        
        # Editor interactivo de datos
        df_directorio_editado = st.data_editor(
            st.session_state.df[cols_directorio],
            num_rows="dynamic",
            use_container_width=True
        )
        if st.button("✏️ Guardar Cambios del Directorio"):
            for col in cols_directorio:
                st.session_state.df[col] = df_directorio_editado[col]
            guardar_datos(st.session_state.df)
            st.success("Información actualizada.")

# --- 3. Pestaña de Importar / Exportar Datos ---
with tab3:
    st.subheader("📥 Exportar Informe")
    if not st.session_state.df.empty:
        csv = st.session_state.df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Descargar Informe Completo (CSV)",
            data=csv,
            file_name=f"asistencia_iglesia_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )

    st.subheader("📤 Importar Base de Datos")
    st.warning("Importar un CSV reemplazará la lista actual.")
    archivo_subido = st.file_uploader("Selecciona el archivo CSV", type=["csv"])
    
    if archivo_subido is not None:
        if st.button("Cargar Datos"):
            try:
                # Se mantiene encoding='utf-8-sig' para evitar errores de formato BOM oculto
                df_importado = pd.read_csv(archivo_subido, sep=None, engine='python', encoding='utf-8-sig')
                
                # Validación de seguridad
                if "Nombre Completo" not in df_importado.columns:
                    st.error("❌ Error: El archivo no tiene el formato correcto. Falta la columna 'Nombre Completo'. Carga cancelada.")
                    st.stop() 

                st.session_state.df = df_importado
                guardar_datos(st.session_state.df)
                st.success("✅ Datos importados exitosamente.")
                st.rerun()

            except Exception as e:
                st.error(f"❌ Ocurrió un error al leer el archivo: {e}")