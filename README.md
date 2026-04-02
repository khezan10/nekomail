🐱 Nekomail - Temporary Email Service
Nekomail adalah layanan email sementara (temporary email) ringan yang dibangun menggunakan Python (FastAPI), SQLite, dan mengandalkan Cloudflare Email Routing beserta Ngrok/Cloudflared tunnel untuk menerima email yang masuk. Dilengkapi dengan sistem login berbasis Linux PAM dan pembersihan database otomatis.

🛠️ Persyaratan Sistem (Requirements)
Sebelum menginstal, pastikan server/laptop kamu memenuhi syarat berikut:

Sistem Operasi Linux (Direkomendasikan Ubuntu/Debian/Armbian, karena sistem login menggunakan modul pam bawaan Linux).
Python 3.8 atau versi lebih baru.
Akun Cloudflare dengan Domain Aktif yang sudah terhubung.
Ngrok atau Cloudflared terinstal di server/laptop kamu untuk mengekspos localhost ke internet publik.

## Modul Python yang Dibutuhkan
Buat file requirements.txt dan isi dengan:
```text
fastapi
uvicorn
pydantic
python-multipart
python-pam
```

## 🚀 Cara Instalasi

**1. Siapkan Folder Proyek**
Pastikan struktur folder kamu persis seperti ini:
```text
/TMAIL
 ├── main.py
 ├── database.py
 ├── crud.py
 ├── cleanup_task.py
 ├── requirements.txt
 └── /frontend
      ├── login.html
      ├── inbox.html
      └── app.js
```

**2. Install Dependencies (Modul Python)**
Buka terminal, masuk ke folder `/TMAIL`, dan jalankan perintah:
```bash
pip install -r requirements.txt
```

**3. Sesuaikan Domain di Frontend**
Buka file `frontend/app.js`, dan ubah baris pertama sesuai dengan domain Cloudflare kamu:
```javascript
const DOMAIN = "@domainkamu.com"; // Ganti dengan domain aslimu
```

---

## ⚙️ Menjalankan Aplikasi & Mengubah Port

Secara bawaan, aplikasi berjalan di port `8000`. Jika kamu ingin mengubah portnya, ada dua cara:

**Cara 1: Melalui Terminal (Disarankan)**
Kamu bisa mengatur port langsung dari perintah Uvicorn saat menyalakan server:
```bash
uvicorn main:app --host 0.0.0.0 --port 8080
```

**Cara 2: Mengubah di file `main.py`**
Buka file `main.py`, scroll ke paling bawah, dan ubah angka portnya, lalu jalankan dengan `python3 main.py`:
```python
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
```

---

## 🌐 Membuka Jalur Internet (Pilih Salah Satu)

Karena webhook Cloudflare butuh URL publik untuk mengirim data email yang masuk, kita harus meng-online-kan port lokal kita. Pilih salah satu metode di bawah ini:

### Opsi A: Menggunakan Ngrok (Mudah & Cepat)
1. Buka terminal baru, jalankan Ngrok ke port aplikasi kamu (misal 8000):
   ```bash
   ngrok http 8000
   ```
2. Salin URL publik dari Ngrok (misal: `https://1234-abcd.ngrok-free.app`). 

### Opsi B: Menggunakan Cloudflared Tunnel (Disarankan & Stabil)
Karena kamu sudah pakai Cloudflare, menggunakan `cloudflared` jauh lebih baik.

**Cara Cepat (Temporary Tunnel):**
```bash
cloudflared tunnel --url [http://127.0.0.1:8000](http://127.0.0.1:8000)
```
*(Salin URL `https://xxxx.trycloudflare.com` yang muncul di terminal).*

**Cara Permanen (Zero Trust Dashboard):**
1. Masuk ke dashboard Cloudflare > **Zero Trust** > **Networks** > **Tunnels**.
2. Buat tunnel baru, instal konektornya di server Linux kamu sesuai perintah yang diberikan.
3. Di bagian **Public Hostname**, atur sub-domain (misal: `api.domainkamu.com`) dan arahkan ke `http://127.0.0.1:8000`.
4. URL publik kamu sekarang adalah `https://api.domainkamu.com`.

---

## ☁️ Setting Cloudflare Worker (Penangkap Email)

Kita perlu membuat Worker di Cloudflare yang bertugas menangkap email dan meneruskannya (forward) ke URL Tunnel (Ngrok/Cloudflared) aplikasi kita.

1. Login ke dashboard Cloudflare, masuk ke menu **Workers & Pages**.
2. Klik tombol **Create Application** lalu pilih **Create Worker**.
3. Beri nama worker kamu (misal: `tmail-forwarder`), lalu klik **Deploy**.
4. Setelah berhasil di-deploy, klik **Edit Code**.
5. Masukkan script JS Worker yang menangkap email dan mengirimkan POST Request (berisi JSON `sender`, `recipient`, `subject`, `body_text`, `body_html`) ke endpoint backend kamu.
   * **PENTING:** Pastikan URL tujuan di dalam script Worker diarahkan ke URL Tunnel kamu ditambah `/webhook/email`.
   * Contoh: `https://api.domainkamu.com/webhook/email` atau `https://1234-abcd.ngrok-free.app/webhook/email`.
6. Klik **Save and Deploy**.

---

## 📧 Konfigurasi Cloudflare Email Routing

Langkah terakhir adalah mengarahkan semua email yang masuk ke domainmu menuju Worker yang baru saja dibuat.

1. Di dashboard Cloudflare, masuk ke menu **Website** dan pilih domain kamu.
2. Klik menu **Email** di sidebar kiri, lalu pilih **Email Routing**.
3. Masuk ke tab **Routing Rules**.
4. Scroll ke bawah cari bagian **Catch-all address**, lalu klik **Edit** (atau **Create** jika belum ada).
5. Pada bagian **Action**, pilih opsi **Send to Worker**.
6. Pada bagian **Destination**, pilih Worker yang baru saja dibuat (`tmail-forwarder`).
7. Klik **Save**.

---

🎉 **Selesai!** Coba kirim email ke alamat acak di domainmu (misal: `meow@domainkamu.com`). Email tersebut akan ditangkap oleh Cloudflare, dilempar ke Worker, masuk ke Tunnel kamu, dan disimpan ke database untuk ditampilkan di website Nekomail!
```
