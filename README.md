# 🚗 Driver Drowsiness Detection System

Sistem deteksi kantuk dan menguap secara *real-time* untuk pengemudi menggunakan Computer Vision. Proyek ini dibangun dengan **Python 3.10**, **Flask**, **MediaPipe**, dan **OpenCV**.

Sistem memantau aliran video dari webcam, menghitung *Eye Aspect Ratio* (EAR) untuk mendeteksi mata tertutup (kantuk), dan *Mouth Aspect Ratio* (MAR) untuk mendeteksi menguap. Jika ambang batas terlampaui, sistem akan memicu peringatan suara.

## 📋 Fitur Utama
- **Real-time Monitoring**: Streaming video langsung ke browser web.
- **Deteksi Kantuk**: Menggunakan perhitungan EAR (*Eye Aspect Ratio*) untuk mendeteksi jika mata tertutup dalam durasi tertentu.
- **Deteksi Menguap**: Menggunakan perhitungan MAR (*Mouth Aspect Ratio*) untuk mendeteksi mulut yang terbuka lebar.
- **Peringatan Suara**: 
  - 🚨 **Alarm**: Berbunyi saat terdeteksi mengantuk.
  - 🎵 **Song**: Berbunyi saat terdeteksi sering menguap (saran istirahat).
- **Visualisasi Mesh**: Menampilkan *landmark* wajah pada video feed.

## 🛠️ Prasyarat & Teknologi

Pastikan kamu menggunakan **Python 3.10**. Library yang digunakan:

* **Flask**: Untuk server web dan streaming video.
* **OpenCV (`cv2`)**: Untuk pengolahan citra.
* **MediaPipe**: Untuk deteksi *landmark* wajah yang presisi.
* **NumPy**: Untuk operasi numerik array.
* **SciPy**: Untuk menghitung jarak Euclidean (EAR/MAR).
* **Pygame**: Untuk memutar file audio/alarm.

## 📂 Struktur Proyek

```text
Deteksi-Ngantuk/
├── templates/
│   └── index.html      # Antarmuka Web
├── app.py              # Logika Utama (Flask & Computer Vision)
├── alarm.mp3           # File audio untuk peringatan kantuk
├── song1.mp3           # File audio untuk peringatan istirahat
└── README.md           # Dokumentasi Proyek
