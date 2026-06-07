# CoffeeShop POS

Aplikasi Point of Sale (POS) untuk CoffeeShop — terdiri dari **Backend API** (FastAPI) dan **Frontend** (Streamlit).

---

## Teknologi

| Layer    | Stack                                      |
|----------|--------------------------------------------|
| Backend  | Python, FastAPI, SQLAlchemy, PostgreSQL     |
| Frontend | Streamlit, Requests                        |
| Auth     | JWT (python-jose), bcrypt (passlib)        |
| Deploy   | Vercel (backend), uv (package manager)     |

---

## Struktur Proyek

```
CoffeShop/
├── app/
│   ├── main.py        # Semua endpoint FastAPI
│   ├── models.py      # Model database SQLAlchemy
│   ├── schemas.py     # Schema Pydantic (request & response)
│   ├── database.py    # Konfigurasi database & session
│   └── auth.py        # JWT, password hashing, dependency auth
├── frontend/
│   ├── main.py        # Halaman login Streamlit
│   ├── pages/
│   │   ├── 1_Dashboard.py          # Analytics (admin only)
│   │   ├── 2_Kasir.py              # Input transaksi (admin & kasir)
│   │   ├── 3_Manajemen_Stok.py     # Kelola menu & user (admin only)
│   │   └── 4_History_Transaksi.py  # Riwayat transaksi (admin & kasir)
│   └── utils/
│       └── api.py     # Helper HTTP call ke backend
├── seed.py            # Script seed database & user default
├── requirements.txt
└── .env
```

---

## Instalasi

### 1. Clone & masuk ke direktori
```powershell
cd CoffeShop
```

### 2. Buat virtual environment & install dependency
```powershell
# Menggunakan uv
uv venv
uv pip install -r requirements.txt
```

Atau menggunakan pip biasa:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Konfigurasi environment
Buat file `.env` di root project:
```env
DATABASE_URL=postgresql://user:password@host:port/dbname
SECRET_KEY=ganti-dengan-string-acak-yang-panjang-dan-aman
```

### 4. Seed database
Membuat tabel, mengisi data menu awal, dan membuat user default:
```powershell
python seed.py
```

User default yang dibuat:
| Username | Password  | Role  |
|----------|-----------|-------|
| admin    | admin123  | admin |
| kasir1   | kasir123  | kasir |

> ⚠️ Segera ganti password setelah pertama kali login.

### 5. Jalankan backend
```powershell
uvicorn app.main:app --reload
```
API tersedia di `http://localhost:8000`

## Autentikasi & Role

Aplikasi menggunakan **JWT Bearer Token** untuk autentikasi. Setiap request ke endpoint yang dilindungi harus menyertakan header:
```
Authorization: Bearer <access_token>
```

### Role & Hak Akses

| Endpoint                  | Admin | Kasir |
|---------------------------|:-----:|:-----:|
| POST /auth/login          | ✅    | ✅    |
| POST /auth/register          | ✅    | ❌    |
| GET /menus                | ✅    | ✅    |
| POST/PATCH/PUT/DELETE /menus | ✅ | ❌    |
| GET/POST /transactions    | ✅    | ✅    |
| GET /analytics/*          | ✅    | ❌    |

---

## Database

Menggunakan **PostgreSQL** (via Supabase atau provider lain). Tabel dibuat otomatis saat server pertama kali dijalankan.

### Model

**User**
| Field           | Tipe    | Keterangan              |
|-----------------|---------|-------------------------|
| id              | integer | primary key             |
| username        | string  | unique                  |
| hashed_password | string  |                         |
| role            | enum    | `admin` atau `kasir`    |
| is_active       | boolean | default `true`          |

**Menu**
| Field  | Tipe    | Keterangan  |
|--------|---------|-------------|
| id     | integer | primary key |
| name   | string  |             |
| price  | integer |             |
| stock  | integer |             |

**Transaction**
| Field       | Tipe     | Keterangan                      |
|-------------|----------|---------------------------------|
| id          | integer  | primary key                     |
| created_at  | datetime | otomatis saat transaksi dibuat  |
| total_price | integer  |                                 |
| details     | relasi   | ke `TransactionDetail`          |

**TransactionDetail**
| Field          | Tipe    | Keterangan              |
|----------------|---------|-------------------------|
| id             | integer | primary key             |
| transaction_id | integer | foreign key → transactions |
| menu_id        | integer | foreign key → menus     |
| qty            | integer |                         |
| subtotal       | integer |                         |

---

## API Endpoints

Base path: `/api/v1`  
Dokumentasi: `http://localhost:8000/docs`

### Auth

#### Login
- **POST** `/api/v1/auth/login`
- Body (form-data): `username`, `password`
- Response:
  ```json
  { "access_token": "<token>", "token_type": "bearer" }
  ```

#### Cek user aktif
- **GET** `/api/v1/auth/me` 🔒
- Response:
  ```json
  { "id": 1, "username": "admin", "role": "admin", "is_active": true }
  ```

#### Buat user baru *(admin only)*
- **POST** `/api/v1/auth/register` 🔒
- Body:
  ```json
  { "username": "kasir2", "password": "pass123", "role": "kasir" }
  ```

---

### Menu

| Method   | URL                          | Auth         | Keterangan         |
|----------|------------------------------|--------------|--------------------|
| GET      | `/api/v1/menus`              | admin, kasir | Ambil semua menu   |
| GET      | `/api/v1/menus/{id}`         | admin, kasir | Ambil menu by ID   |
| POST     | `/api/v1/menus`              | admin        | Tambah menu baru   |
| PATCH    | `/api/v1/menus/{id}`         | admin        | Update menu        |
| PUT      | `/api/v1/menus/{id}/stock`   | admin        | Update stok saja   |
| DELETE   | `/api/v1/menus/{id}`         | admin        | Hapus menu         |

Contoh request POST `/api/v1/menus`:
```json
{ "name": "Espresso", "price": 20000, "stock": 10 }
```

---

### Transaction

| Method | URL                              | Auth         | Keterangan              |
|--------|----------------------------------|--------------|-------------------------|
| POST   | `/api/v1/transactions`           | admin, kasir | Buat transaksi baru     |
| GET    | `/api/v1/transactions`           | admin, kasir | Ambil semua transaksi   |
| GET    | `/api/v1/transactions/{id}`      | admin, kasir | Ambil transaksi by ID   |

Contoh request POST `/api/v1/transactions`:
```json
{
  "items": [
    { "menu_id": 1, "qty": 2 },
    { "menu_id": 3, "qty": 1 }
  ]
}
```

Validasi:
- Menu harus ada
- Stok harus mencukupi (error 400 jika tidak cukup)
- Stok otomatis berkurang setelah transaksi berhasil

---

### Analytics *(admin only)*

| Method | URL                                    | Keterangan                    |
|--------|----------------------------------------|-------------------------------|
| GET    | `/api/v1/analytics/summary`            | Total revenue, transaksi, menu|
| GET    | `/api/v1/analytics/revenue-per-day`    | Revenue harian                |
| GET    | `/api/v1/analytics/total-revenue`      | Total revenue all time        |
| GET    | `/api/v1/analytics/total-transactions` | Total transaksi all time      |
| GET    | `/api/v1/analytics/best-selling-menu`  | 5 menu terlaris               |
| GET    | `/api/v1/analytics/total-sold-per-menu`| Total terjual per menu        |

---

## Error Handling

| Kode | Keterangan                                      |
|------|-------------------------------------------------|
| 400  | Request tidak valid (stok kurang, username duplikat, dsb) |
| 401  | Token tidak ada, tidak valid, atau sudah expired |
| 403  | Token valid tapi role tidak punya akses          |
| 404  | Menu atau transaksi tidak ditemukan              |

---

## Catatan

- Token JWT berlaku selama **8 jam** sejak login.
- `created_at` pada transaksi diisi otomatis oleh server.
- Semua endpoint (kecuali `/` dan `/api/v1/auth/login`) membutuhkan token.
- Untuk mengakses Swagger UI dengan auth: klik tombol **Authorize** di `http://localhost:8000/docs`, lalu masukkan token.
