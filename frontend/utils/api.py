"""Helper functions untuk komunikasi dengan FastAPI backend."""
import requests
import streamlit as st

BASE_URL = "http://localhost:8000/api/v1"


def get_headers() -> dict:
    token = st.session_state.get("token", "")
    return {"Authorization": f"Bearer {token}"}


# ── Auth ─────────────────────────────────────────────────────────────────────

def login(username: str, password: str) -> dict | None:
    try:
        resp = requests.post(
            f"{BASE_URL}/auth/login",
            data={"username": username, "password": password},
            timeout=10,
        )
        if resp.status_code == 200:
            return resp.json()
        return None
    except requests.exceptions.ConnectionError:
        st.error("Tidak bisa terhubung ke server. Pastikan backend sudah berjalan.")
        return None


def get_me() -> dict | None:
    resp = requests.get(f"{BASE_URL}/auth/me", headers=get_headers(), timeout=10)
    return resp.json() if resp.status_code == 200 else None


def register_user(username: str, password: str, role: str) -> tuple[bool, str]:
    resp = requests.post(
        f"{BASE_URL}/auth/register",
        json={"username": username, "password": password, "role": role},
        headers=get_headers(),
        timeout=10,
    )
    if resp.status_code == 201:
        return True, "User berhasil dibuat"
    return False, resp.json().get("detail", "Gagal membuat user")


# ── Menu ─────────────────────────────────────────────────────────────────────

def get_menus() -> list:
    resp = requests.get(f"{BASE_URL}/menus", headers=get_headers(), timeout=10)
    return resp.json() if resp.status_code == 200 else []


def create_menu(name: str, price: int, stock: int) -> tuple[bool, str]:
    resp = requests.post(
        f"{BASE_URL}/menus",
        json={"name": name, "price": price, "stock": stock},
        headers=get_headers(),
        timeout=10,
    )
    if resp.status_code == 201:
        return True, "Menu berhasil ditambahkan"
    return False, resp.json().get("detail", "Gagal menambah menu")


def update_menu(menu_id: int, name: str, price: int, stock: int) -> tuple[bool, str]:
    resp = requests.patch(
        f"{BASE_URL}/menus/{menu_id}",
        json={"name": name, "price": price, "stock": stock},
        headers=get_headers(),
        timeout=10,
    )
    if resp.status_code == 200:
        return True, "Menu berhasil diupdate"
    return False, resp.json().get("detail", "Gagal update menu")


def update_stock(menu_id: int, stock: int) -> tuple[bool, str]:
    resp = requests.put(
        f"{BASE_URL}/menus/{menu_id}/stock",
        json={"stock": stock},
        headers=get_headers(),
        timeout=10,
    )
    if resp.status_code == 200:
        return True, "Stok berhasil diupdate"
    return False, resp.json().get("detail", "Gagal update stok")


def delete_menu(menu_id: int) -> tuple[bool, str]:
    resp = requests.delete(
        f"{BASE_URL}/menus/{menu_id}",
        headers=get_headers(),
        timeout=10,
    )
    if resp.status_code == 200:
        return True, "Menu berhasil dihapus"
    return False, resp.json().get("detail", "Gagal menghapus menu")


# ── Transaction ───────────────────────────────────────────────────────────────

def create_transaction(items: list[dict]) -> tuple[bool, dict | str]:
    resp = requests.post(
        f"{BASE_URL}/transactions",
        json={"items": items},
        headers=get_headers(),
        timeout=10,
    )
    if resp.status_code == 201:
        return True, resp.json()
    return False, resp.json().get("detail", "Gagal membuat transaksi")


def get_transactions() -> list:
    resp = requests.get(f"{BASE_URL}/transactions", headers=get_headers(), timeout=10)
    return resp.json() if resp.status_code == 200 else []


def get_transaction(transaction_id: int) -> dict | None:
    resp = requests.get(
        f"{BASE_URL}/transactions/{transaction_id}",
        headers=get_headers(),
        timeout=10,
    )
    return resp.json() if resp.status_code == 200 else None


# ── Analytics ─────────────────────────────────────────────────────────────────

def get_analytics_summary() -> dict:
    resp = requests.get(
        f"{BASE_URL}/analytics/summary", headers=get_headers(), timeout=10
    )
    return resp.json() if resp.status_code == 200 else {}


def get_revenue_per_day() -> list:
    resp = requests.get(
        f"{BASE_URL}/analytics/revenue-per-day", headers=get_headers(), timeout=10
    )
    return resp.json() if resp.status_code == 200 else []


def get_best_selling() -> list:
    resp = requests.get(
        f"{BASE_URL}/analytics/best-selling-menu", headers=get_headers(), timeout=10
    )
    return resp.json() if resp.status_code == 200 else []


def get_total_sold_per_menu() -> list:
    resp = requests.get(
        f"{BASE_URL}/analytics/total-sold-per-menu", headers=get_headers(), timeout=10
    )
    return resp.json() if resp.status_code == 200 else []
