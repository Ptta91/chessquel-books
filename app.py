import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# CONFIGURACIÓN DE PÁGINA Y ESTILO MEJORADO
st.set_page_config(page_title="Chessquel Books", page_icon="♟️", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .book-card {
        background-color: #1c1f26;
        border-radius: 12px;
        padding: 15px;
        transition: transform .3s;
        border: 1px solid #30363d;
        text-align: center;
        cursor: pointer;
    }
    .book-card:hover {
        transform: translateY(-10px);
        border-color: #ffffff;
        box-shadow: 0px 4px 20px rgba(255,255,255,0.1);
    }
    .stButton>button {
        background-color: #f0f2f6; color: #0e1117;
        border-radius: 8px; font-weight: bold;
    }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# FUNCIÓN PARA REPARAR LINKS DE DRIVE
def fix_drive_link(url):
    if 'drive.google.com' in str(url):
        file_id = url.split('/')[-2] if 'view' in url else url.split('=')[-1]
        return f"https://lh3.googleusercontent.com/d/{file_id}"
    return url

# CONEXIÓN
url_sheet = "https://docs.google.com/spreadsheets/d/1dO1S2Afj7bXDthfAHGueOU-HHpm3BAaqmo0OlvxepsQ/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    data = conn.read(spreadsheet=url_sheet, worksheet="Libros")
    data['URL_Portada'] = data['URL_Portada'].apply(fix_drive_link)
    return data

# --- LÓGICA DE SESIÓN ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'selected_book' not in st.session_state: st.session_state.selected_book = None

if not st.session_state.logged_in:
    st.title("♟️ Chessquel Books")
    with st.form("login_form"):
        u = st.text_input("Email")
        p = st.text_input("Contraseña", type="password")
        if st.form_submit_button("Entrar"):
            if u == "admin@chessquel.com" and p == "1234":
                st.session_state.logged_in = True
                st.rerun()
else:
    df = load_data()

    # MENU SUPERIOR / SIDEBAR
    with st.sidebar:
        st.title("♟️ Chessquel")
        st.write(f"Bienvenido, **Admin**")
        if st.button("Mi Perfil"): st.toast("Próximamente...")
        if st.button("Cerrar Sesión"):
            st.session_state.logged_in = False
            st.rerun()

    # --- CAROUSEL DE NOVEDADES ---
    st.header("✨ Últimos añadidos")
    nov_cols = st.columns(5)
    for i, (_, libro) in enumerate(df.sort_values(by="Fecha_Ingreso", ascending=False).head(5).iterrows()):
        with nov_cols[i]:
            st.image(libro['URL_Portada'], use_container_width=True)
            if st.button(f"Ver: {libro['Titulo']}", key=f"nov_{libro['ID']}"):
                st.session_state.selected_book = libro['ID']

    st.divider()

    # --- CATALOGO COMPLETO ---
    st.header("📚 Explorar Biblioteca")
    col_busq, col_filt1, col_filt2 = st.columns([2,1,1])
    search = col_busq.text_input("Buscar por título o autor...")
    cat_f = col_filt1.multiselect("Categoría", df['Categoria'].unique())
    niv_f = col_filt2.multiselect("Nivel", df['Nivel'].unique())

    # Filtrado
    filt_df = df.copy()
    if search: filt_df = filt_df[filt_df['Titulo'].str.contains(search, case=False) | filt_df['Autor'].str.contains(search, case=False)]
    if cat_f: filt_df = filt_df[filt_df['Categoria'].isin(cat_f)]
    if niv_f: filt_df = filt_df[filt_df['Nivel'].isin(niv_f)]

    # Grid Vertical
    rows = [filt_df.iloc[i:i+4] for i in range(0, len(filt_df), 4)]
    for row in rows:
        cols = st.columns(4)
        for j, (_, libro) in enumerate(row.iterrows()):
            with cols[j]:
                st.markdown(f'<div class="book-card">', unsafe_allow_html=True)
                st.image(libro['URL_Portada'], use_container_width=True)
                st.write(f"**{libro['Titulo']}**")
                st.caption(f"{libro['Nivel']} • {libro['Valoracion']} ⭐")
                if st.button("Detalles", key=f"cat_{libro['ID']}"):
                    st.session_state.selected_book = libro['ID']
                st.markdown('</div>', unsafe_allow_html=True)

    # --- VENTANA DETALLADA (SIDEBAR DERECHO) ---
    if st.session_state.selected_book:
        with st.sidebar:
            st.divider()
            book = df[df['ID'] == st.session_state.selected_book].iloc[0]
            st.image(book['URL_Portada'], use_container_width=True)
            st.title(book['Titulo'])
            st.subheader(f"por {book['Autor']}")
            
            # Tags de Info
            c1, c2 = st.columns(2)
            c1.metric("Nivel", book['Nivel'])
            c2.metric("Páginas", int(book['Paginas']))
            
            st.write(f"**Categoría:** {book['Categoria']}")
            st.write(f"**Valoración:** {book['Valoracion']} ⭐")
            st.write(f"**Lecturas:** {int(book['Veces_Leido'])}")
            
            st.markdown(f"**Sinopsis:**\n{book['Sinopsis']}")
            
            # Estado y Botón
            if book['Estado'] == "Disponible":
                st.success("✅ DISPONIBLE")
                if st.button("SOLICITAR PRÉSTAMO"):
                    st.balloons()
                    st.info("Solicitud enviada al administrador.")
            else:
                st.error(f"🔴 PRESTADO (Poseedor: {book['Poseedor']})")
                st.warning("Hay 2 personas en lista de espera") # Ejemplo estático
                if st.button("ANOTARME EN ESPERA"):
                    st.write("¡Te has anotado correctamente!")

            if st.button("Cerrar Detalle"):
                st.session_state.selected_book = None
                st.rerun()
