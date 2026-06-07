import streamlit as st
import pandas as pd
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.api import get_menus, create_menu, update_menu, update_stock, delete_menu, register_user

st.set_page_config(page_title="Manajemen Stok", page_icon="📦", layout="wide")

# ── Auth guard ────────────────────────────────────────────────────────────────
if not st.session_state.get("token"):
    st.warning("Silakan login terlebih dahulu.")
    st.stop()

user = st.session_state.get("user", {})
if user.get("role") != "admin":
    st.error("⛔ Akses ditolak. Halaman ini hanya untuk Admin.")
    st.stop()

# ── Sidebar info ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"### ☕ CoffeShop POS")
    st.markdown("---")
    st.markdown(f"👤 **{user.get('username', '-')}**")
    st.markdown(f"🏷️ Role: `{user.get('role', '-')}`")

# ── Halaman ───────────────────────────────────────────────────────────────────
st.title("📦 Manajemen Stok & Menu")
st.markdown("---")

tab_menu, tab_stok, tab_user = st.tabs(["☕ Kelola Menu", "🔢 Update Stok", "👥 Kelola User"])

# ═══════════════════════════════════════════════════════════════
# TAB 1 — Kelola Menu
# ═══════════════════════════════════════════════════════════════
with tab_menu:
    menus = get_menus()

    # Tabel menu
    st.subheader("Daftar Menu")
    if menus:
        df = pd.DataFrame(menus)[["id", "name", "price", "stock"]]
        df.columns = ["ID", "Nama Menu", "Harga (Rp)", "Stok"]
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Belum ada menu.")

    st.markdown("---")

    col_add, col_edit, col_del = st.columns(3)

    # Tambah menu
    with col_add:
        st.subheader("➕ Tambah Menu")
        with st.form("form_add_menu"):
            new_name = st.text_input("Nama Menu")
            new_price = st.number_input("Harga (Rp)", min_value=0, step=500)
            new_stock = st.number_input("Stok Awal", min_value=0, step=1)
            if st.form_submit_button("Tambah", use_container_width=True, type="primary"):
                if not new_name:
                    st.error("Nama menu wajib diisi.")
                else:
                    ok, msg = create_menu(new_name, int(new_price), int(new_stock))
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    # Edit menu
    with col_edit:
        st.subheader("✏️ Edit Menu")
        if menus:
            menu_options = {m["name"]: m for m in menus}
            selected_name = st.selectbox("Pilih menu", list(menu_options.keys()), key="sel_edit")
            sel = menu_options[selected_name]
            with st.form("form_edit_menu"):
                edit_name = st.text_input("Nama", value=sel["name"])
                edit_price = st.number_input("Harga (Rp)", value=sel["price"], step=500)
                edit_stock = st.number_input("Stok", value=sel["stock"], step=1)
                if st.form_submit_button("Simpan", use_container_width=True):
                    ok, msg = update_menu(sel["id"], edit_name, int(edit_price), int(edit_stock))
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    # Hapus menu
    with col_del:
        st.subheader("🗑️ Hapus Menu")
        if menus:
            menu_del_options = {m["name"]: m["id"] for m in menus}
            del_name = st.selectbox("Pilih menu", list(menu_del_options.keys()), key="sel_del")
            with st.form("form_del_menu"):
                st.warning(f"Hapus **{del_name}**? Tindakan ini tidak bisa dibatalkan.")
                if st.form_submit_button("Hapus", use_container_width=True):
                    ok, msg = delete_menu(menu_del_options[del_name])
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

# ═══════════════════════════════════════════════════════════════
# TAB 2 — Update Stok
# ═══════════════════════════════════════════════════════════════
with tab_stok:
    st.subheader("🔢 Update Stok Menu")
    menus = get_menus()

    if not menus:
        st.info("Belum ada menu.")
    else:
        # Tampilkan semua menu dengan stok rendah sebagai warning
        low_stock = [m for m in menus if m["stock"] <= 3]
        if low_stock:
            names = ", ".join(m["name"] for m in low_stock)
            st.warning(f"⚠️ Stok menipis: **{names}**")

        st.markdown("---")
        cols = st.columns(3)
        for i, menu in enumerate(menus):
            with cols[i % 3]:
                with st.container(border=True):
                    st.markdown(f"**{menu['name']}**")
                    color = "red" if menu["stock"] == 0 else ("orange" if menu["stock"] <= 3 else "green")
                    st.markdown(f":{color}[Stok saat ini: **{menu['stock']}**]")
                    with st.form(f"stok_form_{menu['id']}"):
                        new_stok = st.number_input(
                            "Stok baru",
                            min_value=0,
                            value=menu["stock"],
                            step=1,
                            key=f"stok_{menu['id']}",
                        )
                        if st.form_submit_button("Update", use_container_width=True):
                            ok, msg = update_stock(menu["id"], int(new_stok))
                            if ok:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)

# ═══════════════════════════════════════════════════════════════
# TAB 3 — Kelola User
# ═══════════════════════════════════════════════════════════════
with tab_user:
    st.subheader("👥 Buat Akun Baru")
    st.markdown("Hanya admin yang dapat membuat akun baru.")
    with st.form("form_add_user"):
        new_uname = st.text_input("Username")
        new_pass = st.text_input("Password", type="password")
        new_role = st.selectbox("Role", ["kasir", "admin"])
        if st.form_submit_button("Buat Akun", use_container_width=True, type="primary"):
            if not new_uname or not new_pass:
                st.error("Username dan password wajib diisi.")
            else:
                ok, msg = register_user(new_uname, new_pass, new_role)
                if ok:
                    st.success(f"✅ {msg} — username: **{new_uname}** | role: **{new_role}**")
                else:
                    st.error(msg)
