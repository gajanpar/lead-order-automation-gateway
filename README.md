# Order & Lead Automation Gateway (Showcase Portfolio)

Arsitektur microservices terintegrasi yang menggabungkan validasi data backend tingkat tinggi menggunakan **FastAPI (Python 3.13)** dan orkestrasi workflow visual menggunakan **n8n**.

Proyek ini dibangun sebagai bukti kemampuan (*proof-of-work*) untuk menyediakan solusi automasi bisnis: dari penerimaan formulir pesanan/prospek, normalisasi nomor kontak WhatsApp, formatting mata uang IDR, hingga penyaluran pesan otomatis ke Google Sheets dan notifikasi instan.

---

## 🏗️ Arsitektur Sistem

```
[ Frontend / Klien / Webhook Sumber ]
                 │ (HTTP POST JSON)
                 ▼
     [ FastAPI Backend Gateway ]  <-- Port 8000 (Pydantic v2 Schema Validation & Clean-up)
                 │
                 ▼ (Internal HTTP Webhook)
         [ n8n Workflow ]         <-- Port 5678 (Formatting, Telegram/WA, Spreadsheet Sync)
```

---

## 🚀 Panduan Menjalankan Sistem

### Opsi A: Menggunakan Docker Compose (Direkomendasikan)
Pastikan Docker Desktop Anda sudah aktif, lalu jalankan:
```bash
docker compose up -d
```
- Dokumentasi API Interaktif (Swagger UI): `http://localhost:8000/docs`
- Antarmuka Visual n8n: `http://localhost:5678`

### Opsi B: Menjalankan FastAPI Mandiri (Local Python)
```bash
cd api
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

---

## 📥 Contoh Request Payload (Test di Swagger atau cURL)

Kirim `POST` ke endpoint `http://localhost:8000/api/v1/orders`:

```json
{
  "customer_name": "Rian Kusuma",
  "customer_email": "rian.kusuma@example.com",
  "customer_whatsapp": "081234567890",
  "service_type": "workflow_automation",
  "budget_estimate_idr": 4500000,
  "notes": "Integrasi sinkronisasi order WhatsApp ke CRM"
}
```

FastAPI akan secara otomatis memformat nomor telepon menjadi standar internasional `+6281234567890`, menghasilkan `tracking_id` unik, dan meneruskannya ke antrian n8n.
