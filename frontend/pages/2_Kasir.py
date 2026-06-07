import streamlit as st
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.api import get_menus, create_transaction

st.set_page_config(page_title="Kasir", page_icon="🧾", layout="wide")

# ── Auth guard ────────────────────────────────────────────────────────────────
if not st.session_state.get("token"):
    st.warning("Silakan login terlebih dahulu.")
    st.stop()

user = st.session_state.get("user", {})
if user.get("role") not in ("admin", "kasir"):
    st.error("⛔ Akses ditolak.")
    st.stop()

# ── Sidebar info ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"### ☕ CoffeShop POS")
    st.markdown("---")
    st.markdown(f"👤 **{user.get('username', '-')}**")
    st.markdown(f"🏷️ Role: `{user.get('role', '-')}`")

# ── Session cart ──────────────────────────────────────────────────────────────
if "cart" not in st.session_state:
    st.session_state.cart = {}  # {menu_id: {"name": .., "price": .., "qty": ..}}

# ── Halaman ───────────────────────────────────────────────────────────────────
st.title("🧾 Kasir — Input Transaksi")
st.markdown("---")

menus = get_menus()

if not menus:
    st.warning("Tidak ada menu tersedia.")
    st.stop()

# ── Pilih menu ────────────────────────────────────────────────────────────────
st.subheader("☕ Pilih Menu")
cols = st.columns(3)

for i, menu in enumerate(menus):
    with cols[i % 3]:
        with st.container(border=True):
            st.markdown(f"**{menu['name']}**")
            st.markdown(f"Rp {menu['price']:,.0f}".replace(",", "."))
            stok_label = f"Stok: {menu['stock']}"
            if menu["stock"] == 0:
                st.markdown(f":red[{stok_label}]")
            elif menu["stock"] <= 3:
                st.markdown(f":orange[{stok_label}]")
            else:
                st.markdown(f":green[{stok_label}]")

            if menu["stock"] > 0:
                qty = st.number_input(
                    "Qty",
                    min_value=0,
                    max_value=menu["stock"],
                    value=st.session_state.cart.get(menu["id"], {}).get("qty", 0),
                    key=f"qty_{menu['id']}",
                    label_visibility="collapsed",
                )
                if qty > 0:
                    st.session_state.cart[menu["id"]] = {
                        "name": menu["name"],
                        "price": menu["price"],
                        "qty": qty,
                    }
                elif menu["id"] in st.session_state.cart:
                    del st.session_state.cart[menu["id"]]
            else:
                st.button("Habis", disabled=True, key=f"btn_{menu['id']}")

st.markdown("---")

# ── Keranjang ─────────────────────────────────────────────────────────────────
st.subheader("🛒 Keranjang")

cart = {k: v for k, v in st.session_state.cart.items() if v["qty"] > 0}

if not cart:
    st.info("Keranjang kosong. Pilih menu di atas.")
else:
    total = 0
    rows = []
    for menu_id, item in cart.items():
        subtotal = item["price"] * item["qty"]
        total += subtotal
        rows.append({
            "Menu": item["name"],
            "Harga": f"Rp {item['price']:,.0f}".replace(",", "."),
            "Qty": item["qty"],
            "Subtotal": f"Rp {subtotal:,.0f}".replace(",", "."),
        })

    import pandas as pd
    df_cart = pd.DataFrame(rows)
    st.dataframe(df_cart, use_container_width=True, hide_index=True)

    st.markdown(f"### Total: **Rp {total:,.0f}**".replace(",", "."))

    col_bayar, col_reset = st.columns([1, 1])
    with col_bayar:
        if st.button("✅ Proses Transaksi", use_container_width=True, type="primary"):
            items_payload = [
                {"menu_id": mid, "qty": data["qty"]}
                for mid, data in cart.items()
            ]
            with st.spinner("Memproses transaksi..."):
                ok, result = create_transaction(items_payload)

            if ok:
                st.session_state.cart = {}
                st.success(
                    f"✅ Transaksi berhasil! ID: **#{result['id']}** | "
                    f"Total: **Rp {result['total_price']:,.0f}**".replace(",", ".")
                )
                st.rerun()
            else:
                st.error(f"❌ Gagal: {result}")

    with col_reset:
        if st.button("🗑️ Kosongkan Keranjang", use_container_width=True):
            st.session_state.cart = {}
            st.rerun()
