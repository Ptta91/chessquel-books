import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA (Debe ser lo primero)
st.set_page_config(page_title="Chessquel Books", page_icon="♟️", layout="wide")

# 2. ESTILOS CSS PARA ESTÉTICA PREMIUM (Opción A: Negro y Plata)
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .book-card {
        background-color: #1c1f26;
        border-radius: 12px;
        padding: 15px;
        border: 1px solid #30363d;
        text-align: center;
        margin-bottom: 20px;
    }
    .stButton>button {
        background-color: #f0f2f6; color: #0e1117;
        border-radius: 8px; font-weight: bold; width: 100%;
    }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# 3. FUNCIÓN DE IMÁGENES INTELIGENTE
def get_image_url(url):
    url = str(url)
    if 'drive.google.com' in url:
        try:
            if '/d/' in url: file_id = url.split('/d/')[1].split('/')[0]
            else: file_id = url.split('id=')[1].split('&')[0]
            return f"https://drive.google.com/thumbnail?id={file_id}&sz=w600"
        except: return "https://via.placeholder.com/150?text=Error+Link"
    # Si es un link de Amazon o externo, lo deja tal cual
    return url

# 4. CARGA DE DATOS (CSV Export)
URL_CSV = "https://docs.google.com/spreadsheets/d/1dO1S2Afj7bXDthfAHGueOU-HHpm3BAaqmo0OlvxepsQ/export?format=csv&gid=0"

@st.cache_data(ttl=300) # Cache de 5 minutos
def load_library():
    df = pd.read_csv(URL_CSV)
    df['URL_Portada'] = df['URL_Portada'].apply(get_image_url)
    return df

# 5. LÓGICA DE LOGIN (Persistente durante la sesión)
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("♟️ Chessquel Books")
    st.subheader("Inicia sesión para acceder al catálogo")
    with st.form("login_form"):
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        if st.form_submit_button("Entrar"):
            # Credencial temporal (Pronto usaremos tu pestaña de Usuarios)
            if u == "admin@chessquel.com" and p == "1234":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Credenciales incorrectas")
else:
    # --- APP PRINCIPAL ---
    try:
        df = load_library()
        
        # BARRA LATERAL
        with st.sidebar:
            st.title("Chessquel Books")
            st.write("---")
            st.button("👤 Mi Perfil")
            if st.button("🚪 Cerrar Sesión"):
                st.session_state.auth = False
                st.rerun()

        # BUSCADOR Y FILTROS
        st.title("📚 Biblioteca Chessquel")
        col_s, col_f = st.columns([2, 1])
        search = col_s.text_input("Buscar por título o autor...")
        
        # Grid de Libros
        display_df = df.copy()
        if search:
            display_df = display_df[display_df['Titulo'].str.contains(search, case=False) | 
                                    display_df['Autor'].str.contains(search, case=False)]

        rows = [display_df.iloc[i:i+4] for i in range(0, len(display_df), 4)]
        
        for row in rows:
            cols = st.columns(4)
            for i, (_, libro) in enumerate(row.iterrows()):
                with cols[i]:
                    st.markdown('<div class="book-card">', unsafe_allow_html=True)
                    st.image(libro['URL_Portada'], use_container_width=True)
                    st.write(f"**{libro['Titulo']}**")
                    st.caption(f"{libro['Nivel']} • ⭐ {libro['Valoracion']}")
                    
                    if st.button("Ver Ficha", key=f"btn_{libro['ID']}"):
                        st.session_state.detail = libro['ID']
                    st.markdown('</div>', unsafe_allow_html=True)

        # VENTANA DE DETALLES (Sidebar)
        if 'detail' in st.session_state and st.session_state.detail:
            with st.sidebar:
                st.write("---")
                det = df[df['ID'] == st.session_state.detail].iloc[0]
                st.image(det['URL_Portada'], use_container_width=True)
                st.subheader(det['Titulo'])
                st.write(f"**Autor:** {det['Autor']}")
                st.write(f"**Estado:** {det['Estado']}")
                st.write(f"**Sinopsis:** {det['Sinopsis']}")
                if st.button("Cerrar Detalle"):
                    st.session_state.detail = None
                    st.rerun()

    except Exception as e:
        st.error(f"Error cargando datos: {e}")
