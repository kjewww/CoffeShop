import streamlit as st
import pandas as pd
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.api import (
    get_analytics_summary,
    get_revenue_per_day,
    get_best_selling,
    get_total_sold_per_menu,
)

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

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
st.title("📊 Dashboard Analytics")
st.markdown("---")

# Summary cards
summary = get_analytics_summary()
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(
        "💰 Total Revenue",
        f"Rp {summary.get('total_revenue', 0):,.0f}".replace(",", "."),
    )
with col2:
    st.metric("🧾 Total Transaksi", summary.get("total_transactions", 0))
with col3:
    st.metric("☕ Total Menu", summary.get("total_menus", 0))

st.markdown("---")

# Revenue per day chart
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📈 Revenue Per Hari")
    rev_data = get_revenue_per_day()
    if rev_data:
        df_rev = pd.DataFrame(rev_data)
        df_rev["date"] = pd.to_datetime(df_rev["date"])
        df_rev = df_rev.sort_values("date")
        df_rev = df_rev.rename(columns={"date": "Tanggal", "total_revenue": "Revenue (Rp)"})
        st.line_chart(df_rev.set_index("Tanggal")["Revenue (Rp)"])
    else:
        st.info("Belum ada data transaksi.")

with col_right:
    st.subheader("🏆 5 Menu Terlaris")
    best = get_best_selling()
    if best:
        df_best = pd.DataFrame(best)
        df_best = df_best.rename(
            columns={"menu_name": "Menu", "total_sold": "Terjual"}
        )
        st.bar_chart(df_best.set_index("Menu")["Terjual"])
    else:
        st.info("Belum ada data penjualan.")

st.markdown("---")

# Total sold per menu table
st.subheader("📋 Total Penjualan Per Menu")
sold = get_total_sold_per_menu()
if sold:
    df_sold = pd.DataFrame(sold)
    df_sold = df_sold.rename(columns={"menu_name": "Menu", "total_sold": "Total Terjual"})
    df_sold = df_sold.sort_values("Total Terjual", ascending=False).reset_index(drop=True)
    df_sold.index += 1
    st.dataframe(df_sold, use_container_width=True)
else:
    st.info("Belum ada data penjualan.")
