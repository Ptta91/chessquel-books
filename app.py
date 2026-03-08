import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# CONFIGURACIÓN DE PÁGINA Y ESTILO "SOFTR/NETFLIX"
st.set_page_config(page_title="Chessquel Books", page_icon="♟️", layout="wide")

st.markdown("""
    <style>
    /* Fondo oscuro y tipografía */
    .stApp { background-color: #0e1117; color: #ffffff; }
    
    /* Estilo de Tarjetas tipo Netflix */
    .book-card {
        background-color: #1c1f26;
        border-radius: 10px;
        padding: 10px;
        transition: transform .2s;
        border: 1px solid #30363d;
        height: 100%;
    }
    .book-card:hover {
        transform: scale(1.05);
        border-color: #ffffff;
    }
    
    /* Scroll Horizontal Custom */
    .horizontal-scroll {
        display: flex;
        overflow-x: auto;
        gap: 20px;
        padding: 10px 0;
    }
    .horizontal-scroll::-webkit-scrollbar { height: 8px; }
    .horizontal-scroll::-webkit-scrollbar-thumb { background: #30363d; border-radius: 10px; }
    
    /* Botones Estilo Plata */
    .stButton>button {
        background-color: #f0f2f6; color: #0e1117;
        border-radius: 5px; font-weight: bold; width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# CONEXIÓN A GOOGLE SHEETS
url = "https://docs.google.com/spreadsheets/d/1dO1S2Afj7bXDthfAHGueOU-HHpm3BAaqmo0OlvxepsQ/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    return conn.read(spreadsheet=url, usecols=list(range(14)))

# --- SISTEMA DE LOGIN (SIMPLIFICADO PARA INICIO) ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("♟️ Chessquel Books")
    st.subheader("Acceso a la Biblioteca")
    with st.form("login"):
        user_email = st.text_input("Email")
        user_pass = st.text_input("Contraseña", type="password")
        if st.form_submit_button("Entrar"):
            # Aquí luego validaremos contra tu pestaña de Usuarios
            # Por ahora, acceso de prueba:
            if user_email == "admin@chessquel.com" and user_pass == "1234":
                st.session_state.logged_in = True
                st.session_state.role = "admin"
                st.rerun()
            else:
                st.error("Credenciales no encontradas o incorrectas.")
else:
    # --- APP PRINCIPAL ---
    df = load_data()

    # Sidebar / Menú Superior
    st.sidebar.title("Chessquel Books")
    st.sidebar.button("Mi Perfil")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.logged_in = False
        st.rerun()

    # Sección 1: Últimos Añadidos (Scroll Horizontal)
    st.markdown("### ✨ Últimos libros añadidos")
    novedades = df.sort_values(by="Fecha_Ingreso", ascending=False).head(10)
    
    cols = st.columns(5)
    for i, (_, libro) in enumerate(novedades.iterrows()):
        with cols[i % 5]:
            st.markdown(f"""
                <div class="book-card">
                    <img src="{libro['URL_Portada']}" style="width:100%; border-radius:5px;">
                    <p style="margin-top:10px; font-weight:bold; font-size:14px;">{libro['Titulo']}</p>
                    <p style="font-size:12px; color:#8b949e;">{libro['Autor']}</p>
                    <p style="font-size:11px; background:#30363d; display:inline-block; padding:2px 5px; border-radius:3px;">{libro['Nivel']}</p>
                </div>
                """, unsafe_allow_html=True)
            if st.button("Ver detalle", key=f"det_{libro['ID']}"):
                st.session_state.selected_book = libro['ID']

    st.divider()

    # Sección 2: Todos los libros (Catálogo Vertical con Filtros)
    st.markdown("### 📚 Catálogo Completo")
    
    # Filtros
    f_cat = st.multiselect("Categoría", df['Categoria'].unique())
    f_niv = st.multiselect("Nivel", df['Nivel'].unique())
    
    display_df = df.copy()
    if f_cat: display_df = display_df[display_df['Categoria'].isin(f_cat)]
    if f_niv: display_df = display_df[display_df['Nivel'].isin(f_niv)]

    # Mostrar en Grid
    items_per_row = 4
    for i in range(0, len(display_df), items_per_row):
        row_items = display_df.iloc[i : i + items_per_row]
        cols = st.columns(items_per_row)
        for j, (_, libro) in enumerate(row_items.iterrows()):
            with cols[j]:
                st.image(libro['URL_Portada'], use_container_width=True)
                st.write(f"**{libro['Titulo']}**")
                st.caption(f"{libro['Autor']} • {libro['Valoracion']} ⭐")
                if st.button("Detalle", key=f"cat_{libro['ID']}"):
                    st.info(f"Abriendo detalle de: {libro['Titulo']}")
