import streamlit as st
from utils.api import login, get_me

st.set_page_config(
    page_title="CoffeShop POS",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session state init ────────────────────────────────────────────────────────
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None


def do_logout():
    st.session_state.token = None
    st.session_state.user = None
    st.rerun()


# ── Login form ────────────────────────────────────────────────────────────────
if not st.session_state.token:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("## ☕ CoffeShop POS")
        st.markdown("---")
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="admin / kasir1")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", use_container_width=True)

        if submitted:
            if not username or not password:
                st.error("Username dan password wajib diisi.")
            else:
                with st.spinner("Logging in..."):
                    result = login(username, password)
                if result:
                    st.session_state.token = result["access_token"]
                    st.session_state.user = get_me()
                    st.rerun()
                else:
                    st.error("Username atau password salah.")
else:
    # Sudah login → tampilkan info di sidebar dan arahkan ke halaman utama
    user = st.session_state.user or {}
    role = user.get("role", "")

    with st.sidebar:
        st.markdown(f"### ☕ CoffeShop POS")
        st.markdown("---")
        st.markdown(f"👤 **{user.get('username', '-')}**")
        st.markdown(f"🏷️ Role: `{role}`")
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            do_logout()

    st.markdown("## Selamat datang di CoffeShop POS ☕")
    st.markdown(
        "Gunakan menu di **sidebar kiri** untuk navigasi ke halaman yang diinginkan."
    )

    if role == "admin":
        st.info(
            "Kamu login sebagai **Admin** — akses penuh ke semua halaman.",
            icon="🔑",
        )
    else:
        st.info(
            "Kamu login sebagai **Kasir** — akses ke halaman Kasir dan History Transaksi.",
            icon="🧾",
        )
