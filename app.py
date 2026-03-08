import streamlit as st
import pandas as pd

# CONFIGURACIÓN BÁSICA
st.set_page_config(page_title="Chessquel Books", page_icon="♟️", layout="wide")

# ESTILOS CSS
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    [data-testid="stMetricValue"] { color: #ffffff !important; }
    .book-card {
        background-color: #1c1f26;
        border-radius: 12px;
        padding: 10px;
        border: 1px solid #30363d;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# FUNCIÓN REPARAR DRIVE
def fix_drive_link(url):
    if 'drive.google.com' in str(url):
        try:
            if '/d/' in url: file_id = url.split('/d/')[1].split('/')[0]
            else: file_id = url.split('id=')[1].split('&')[0]
            return f"https://drive.google.com/thumbnail?id={file_id}&sz=w600"
        except: return "https://via.placeholder.com/150" # Imagen por defecto si falla
    return url

# CONEXIÓN DIRECTA (Más estable que la librería GSheets para lectura rápida)
URL_CSV = "https://docs.google.com/spreadsheets/d/1dO1S2Afj7bXDthfAHGueOU-HHpm3BAaqmo0OlvxepsQ/export?format=csv&gid=0"

@st.cache_data(ttl=600) # Guarda los datos 10 min para no saturar a Google
def get_data():
    df = pd.read_csv(URL_CSV)
    df['URL_Portada'] = df['URL_Portada'].apply(fix_drive_link)
    return df

# --- LOGIN ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("♟️ Chessquel Books")
    u = st.text_input("Usuario (Email)")
    p = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        if u == "admin@chessquel.com" and p == "1234":
            st.session_state.logged_in = True
            st.rerun()
        else: st.error("Error de acceso")
else:
    # --- APP ---
    try:
        df = get_data()
        st.sidebar.title("Chessquel Books")
        if st.sidebar.button("Cerrar Sesión"):
            st.session_state.logged_in = False
            st.rerun()

        # Buscador
        search = st.text_input("🔍 Buscar libro...")
        if search:
            df = df[df['Titulo'].str.contains(search, case=False) | df['Autor'].str.contains(search, case=False)]

        # Grid
        cols = st.columns(4)
        for i, (_, libro) in enumerate(df.iterrows()):
            with cols[i % 4]:
                st.markdown('<div class="book-card">', unsafe_allow_html=True)
                st.image(libro['URL_Portada'], use_container_width=True)
                st.write(f"**{libro['Titulo']}**")
                st.caption(f"{libro['Nivel']}")
                if st.button("Ver ficha", key=f"btn_{libro['ID']}"):
                    st.info(f"Sinopsis: {libro['Sinopsis']}")
                st.markdown('</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error cargando base de datos. Verifica el link del Excel.")
