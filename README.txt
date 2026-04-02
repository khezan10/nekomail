Langkah 1: Buka Jalur Internet dengan Ngrok
Karena aplikasimu masih berjalan di 127.0.0.1:8000 (hanya bisa diakses laptopmu), kita butuh Ngrok untuk membuat link publik.

Buka web ngrok.com, daftar akun gratis, dan download aplikasinya untuk Windows.
Ekstrak file zip-nya, kamu akan mendapat satu file bernama ngrok.exe.
Klik dua kali ngrok.exe (akan terbuka terminal hitam baru).
Di dashboard web Ngrok (menu Your Authtoken), copy perintah auth-nya dan paste ke terminal Ngrok, lalu tekan Enter. Contoh:
ngrok config add-authtoken 1a2b3c4d5e...
Terakhir, jalankan perintah ini untuk membuka jalan ke aplikasimu:
ngrok http 8000
Tunggu beberapa detik, Ngrok akan memunculkan tulisan Forwarding. Copy link yang berawalan https://... tersebut (misal: https://1234-abcd.ngrok-free.app).





ngrok http 8000




Langkah 2: Buat "Penangkap Email" di Cloudflare (Worker)
Sekarang kita beri tahu Cloudflare: "Hei, kalau ada email masuk ke domainku, tolong lempar datanya ke link Ngrok tadi!"

Login ke dashboard Cloudflare, masuk ke menu Workers & Pages.
Klik tombol Create Application lalu pilih Create Worker.
Beri nama (misal: tmail-forwarder), lalu klik Deploy.
Setelah berhasil, klik Edit Code.





Langkah 3: Aktifkan Rute Email di Domainmu
Langkah terakhir, kita aktifkan fiturnya di domain kamu.

Di dashboard Cloudflare, masuk ke menu Website dan pilih domain kamu.
Klik menu Email di sebelah kiri, lalu pilih Email Routing.
Masuk ke tab Routing Rules.
Scroll ke bawah cari bagian Catch-all address, klik Edit (atau Create jika belum ada).
Pada bagian Action, pilih Send to Worker.
Pada bagian Destination, pilih Worker yang baru saja kita buat tadi (tmail-forwarder).
Klik Save.