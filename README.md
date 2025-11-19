# Dining Philosophers Simulation

## Tentang Proyek
Simulasi visual interaktif ini dibuat untuk memecahkan dan memvisualisasikan **Masalah Dining Philosophers** yang merupakan masalah klasik dalam ilmu komputer, khususnya yang berkaitan dengan **sinkronisasi** dan **penanganan deadlock** dalam sistem operasi.

---

## Apa itu Masalah Dining Philosophers?
Masalah **Dining Philosophers** dicetuskan oleh Edsger Dijkstra pada tahun 1965. Ini adalah sebuah ilustrasi bagaimana **sumber daya bersama** (sumpit) dapat menyebabkan **deadlock** dan **starvation** dalam sistem konkurensi (multi-threading).

### Skenario:
* **5** filsuf duduk mengelilingi meja bundar.
* Setiap filsuf bergantian antara **berpikir** dan **makan**.
* Terdapat **5 sumpit**, satu di antara setiap pasang filsuf.
* Untuk makan, seorang filsuf **membutuhkan 2 sumpit** (satu di sebelah kiri dan satu di sebelah kanan).

### Masalah yang Dipecahkan:
| Masalah | Deskripsi |
| :--- | :--- |
| **Deadlock** | Kondisi di mana semua filsuf mengambil satu sumpit dan menunggu sumpit yang lain, sehingga tidak ada yang bisa makan. |
| **Starvation** | Kondisi di mana beberapa filsuf tidak pernah bisa mendapatkan kedua sumpitnya untuk makan, sementara yang lain terus-menerus makan. |
| **Race Condition** | Kompetisi untuk mengakses sumpit, yang merupakan sumber daya bersama (shared resource). |

---

## Fitur Simulasi
Simulasi ini menawarkan antarmuka yang lengkap untuk memahami masalah dan solusinya:

### Kontrol Interaktif
* **Start/Pause/Reset** simulasi.
* **Pengaturan kecepatan** simulasi (0.5x - 3x).
* **Pemilihan solusi algoritma** secara *on-the-fly*.

### Tiga Solusi yang Diimplementasikan
1.  **Solusi Asimetrik (Ganjil-Genap):** Filsuf diberi aturan pengambilan sumpit yang berbeda berdasarkan indeksnya. (Contoh: Ganjil ambil kiri-kanan, Genap ambil kanan-kiri).
2.  **Solusi 4 Filsuf Saja:** Membatasi jumlah filsuf yang boleh mencoba makan secara bersamaan (maksimal 4), diimplementasikan menggunakan **Semaphore**.
3.  **Solusi Passing Token:** Hanya filsuf yang memegang 'token' yang diizinkan untuk mengambil sumpit dan makan.

### Visualisasi Real-time
* Status setiap filsuf (**Thinking, Hungry, Eating**).
* **Counter** jumlah makan setiap filsuf.
* **Log aktivitas** detail dengan *timestamp*.
* Animasi yang *smooth* dan *responsive design*.

---

## Teknologi yang Digunakan
* **Backend:** **Python 3** dengan **Flask** (untuk REST API) dan **Threading** (untuk simulasi konkurensi).
* **Frontend:** **HTML5, CSS3, JavaScript vanilla**.
    * **Tailwind CSS** untuk styling.
    * Font Awesome & Google Fonts (Poppins).
* **Deployment Ready:** Struktur proyek Flask yang terorganisir dan *responsive design*.

---

## Tim Pengembang
### Es Pisang Ijo Gapake Keju

| NIM | Nama |
| :---: | :--- |
| 103012580001 | Debby Lelyca Rohdearni Damanik |
| 103012580032 | Dianne Dini Al-haq |
| 103012580054 | Giyats Almanfalutti |
| 103012580005 | Hafizh Dhiya Ulhaq |

---

## Cara Menjalankan
### Prerequisites
* Python 3.8+
* `pip` (Python package manager)

### Installation & Running
```bash
# Clone repository
git clone https://github.com/debbylelycaa/dining-philosophers-simulation.git
cd dining-philosophers-simulation

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py

# Buka browser: http://localhost:5000