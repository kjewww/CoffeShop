import streamlit as st
import pandas as pd
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.api import get_transactions, get_transaction, get_menus

st.set_page_config(page_title="History Transaksi", page_icon="📜", layout="wide")

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

# ── Halaman ───────────────────────────────────────────────────────────────────
st.title("📜 History Transaksi")
st.markdown("---")

transactions = get_transactions()

if not transactions:
    st.info("Belum ada transaksi.")
    st.stop()

# Buat lookup nama menu
menus = get_menus()
menu_map = {m["id"]: m["name"] for m in menus}

# ── Tabel ringkasan ───────────────────────────────────────────────────────────
df = pd.DataFrame([
    {
        "ID": t["id"],
        "Waktu": pd.to_datetime(t["created_at"]).strftime("%d %b %Y %H:%M"),
        "Total (Rp)": t["total_price"],
        "Jumlah Item": sum(d["qty"] for d in t["details"]),
    }
    for t in transactions
])
df = df.sort_values("ID", ascending=False).reset_index(drop=True)

# Filter tanggal
col_filter, col_spacer = st.columns([2, 3])
with col_filter:
    filter_date = st.date_input("Filter tanggal", value=None, label_visibility="visible")

if filter_date:
    filter_str = filter_date.strftime("%d %b %Y")
    df = df[df["Waktu"].str.startswith(filter_str)]

st.markdown(f"**{len(df)} transaksi ditemukan**")
st.dataframe(
    df.style.format({"Total (Rp)": lambda x: f"Rp {x:,.0f}".replace(",", ".")}),
    use_container_width=True,
    hide_index=True,
)

st.markdown("---")

# ── Detail transaksi ──────────────────────────────────────────────────────────
st.subheader("🔍 Detail Transaksi")

if transactions:
    trx_ids = [t["id"] for t in sorted(transactions, key=lambda x: x["id"], reverse=True)]
    selected_id = st.selectbox(
        "Pilih ID Transaksi",
        trx_ids,
        format_func=lambda x: f"Transaksi #{x}",
    )

    detail = get_transaction(selected_id)
    if detail:
        st.markdown(
            f"🕒 **Waktu:** {pd.to_datetime(detail['created_at']).strftime('%d %b %Y %H:%M')}"
        )

        detail_rows = [
            {
                "Menu": menu_map.get(d["menu_id"], f"Menu #{d['menu_id']}"),
                "Qty": d["qty"],
                "Subtotal": f"Rp {d['subtotal']:,.0f}".replace(",", "."),
            }
            for d in detail["details"]
        ]
        df_detail = pd.DataFrame(detail_rows)
        st.dataframe(df_detail, use_container_width=True, hide_index=True)

        st.markdown(
            f"### 💰 Total: **Rp {detail['total_price']:,.0f}**".replace(",", ".")
        )
