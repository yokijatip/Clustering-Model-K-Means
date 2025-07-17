# Worker Performance Analysis - K-means Clustering Model

Model machine learning untuk menganalisis performa karyawan menggunakan algoritma K-means clustering yang dapat diintegrasikan dengan aplikasi Android Kotlin.

## 🎯 Fitur

- **K-means Clustering**: Mengelompokkan karyawan menjadi 3 kategori (High, Medium, Low Performer)
- **Multi-metric Analysis**: Menganalisis berdasarkan attendance rate, work hours, punctuality, dan consistency
- **TensorFlow Lite Support**: Model dapat dijalankan di Android dengan TFLite
- **Firebase Integration**: Mengambil data langsung dari Firestore
- **Visualisasi**: Grafik dan chart untuk analisis performa

## 📊 Metrics yang Dianalisis

1. **Attendance Rate** (30%): Persentase kehadiran dalam periode tertentu
2. **Average Work Hours** (25%): Rata-rata jam kerja per hari
3. **Punctuality Score** (25%): Skor ketepatan waktu masuk/keluar
4. **Consistency Score** (20%): Konsistensi jam kerja

## 🚀 Setup dan Instalasi

### 1. Persiapan Environment

```bash
# Clone atau download project ini
# Buat virtual environment
python -m venv venv

# Aktivasi virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Konfigurasi Firebase

1. Download service account key dari Firebase Console
2. Simpan sebagai `firebase-credentials.json` di root folder
3. Copy `.env.example` menjadi `.env`
4. Update path credentials di `.env`

```bash
cp .env.example .env
```

### 3. Struktur Data Firestore

Pastikan Firestore memiliki struktur berikut:

**Collection: `users`**

```json
{
  "userId": "string",
  "name": "string",
  "email": "string",
  "role": "string", // "admin" atau "worker"
  "workerId": "string"
}
```

**Collection: `attendance`**

```json
{
  "attendanceId": "string",
  "userId": "string",
  "date": "string", // "YYYY-MM-DD"
  "clockInTime": "string", // ISO timestamp
  "clockOutTime": "string", // ISO timestamp
  "workMinutes": "number",
  "overtimeMinutes": "number",
  "status": "string" // "approved", "pending", etc.
}
```

## 🔧 Cara Menjalankan

### Training Model

```bash
python main.py
```

Script ini akan:

1. Mengambil data dari Firestore
2. Memproses data untuk clustering
3. Melatih model K-means
4. Membuat visualisasi
5. Menyimpan model dalam format joblib dan TFLite
6. Membuat metadata untuk integrasi Android

### Output Files

Setelah training berhasil, akan dibuat files:

```
models/
├── kmeans_worker_model.joblib      # Model scikit-learn
├── scaler.joblib                   # StandardScaler
├── worker_analysis_model.tflite    # Model TensorFlow Lite
├── model_metadata.json             # Metadata model
└── tflite_model_info.json         # Info untuk Android

cluster_visualization.png           # Visualisasi hasil clustering
training.log                       # Log training process
```

## 📱 Integrasi dengan Android

### 1. Copy Files ke Android Project

Copy files berikut ke folder `assets` Android project:

- `models/worker_analysis_model.tflite`
- `models/tflite_model_info.json`

### 2. Dependencies Android

Tambahkan di `build.gradle` (app level):

```gradle
implementation 'org.tensorflow:tensorflow-lite:2.13.0'
implementation 'org.tensorflow:tensorflow-lite-support:0.4.4'
```

### 3. Contoh Penggunaan di Kotlin

```kotlin
// Load model info
val modelInfo = loadModelInfo()

// Prepare input features
val features = floatArrayOf(
    attendanceRate,    // 0-100
    avgWorkHours,      // 0-24
    punctualityScore,  // 0-100
    consistencyScore   // 0-100
)

// Run inference
val cluster = runInference(features)
val performanceLabel = getPerformanceLabel(cluster)
```

## 🔍 Monitoring dan Debugging

### Logs

Training process akan menghasilkan log detail di:

- Console output
- `training.log` file

### Troubleshooting

**Error: Firebase credentials not found**

```bash
# Pastikan file firebase-credentials.json ada
# Update path di .env file
```

**Error: No data found**

```bash
# Cek koneksi Firestore
# Pastikan ada data di collection users dan attendance
# Cek filter tanggal (default: 30 hari terakhir)
```

**Error: TFLite conversion failed**

```bash
# Pastikan TensorFlow versi compatible
# Cek apakah model scikit-learn berhasil disimpan
```

## 📈 Interpretasi Hasil

### Performance Labels

- **High Performer**: Attendance tinggi, jam kerja optimal, punctual, konsisten
- **Medium Performer**: Performa rata-rata di sebagian besar metrics
- **Low Performer**: Perlu improvement di beberapa area

### Cluster Analysis

Model akan menampilkan:

- Distribusi karyawan per kategori
- Rata-rata metrics per kategori
- Visualisasi clustering
- Silhouette score untuk evaluasi model

## 🛠 Customization

### Mengubah Weights Features

Edit di `config.py`:

```python
FEATURE_WEIGHTS = {
    'attendance_rate': 0.4,      # Increase attendance importance
    'avg_work_hours': 0.2,
    'punctuality_score': 0.3,
    'consistency_score': 0.1
}
```

### Mengubah Jumlah Cluster

```python
N_CLUSTERS = 4  # Untuk 4 kategori performance
```

### Mengubah Periode Analisis

```python
# Di main.py, ubah parameter days_back
workers_df, attendance_df = firebase_client.get_worker_performance_data(days_back=60)
```

## 📝 Next Steps

1. **Training Model**: Jalankan script untuk membuat model
2. **Validasi Hasil**: Cek visualisasi dan metrics
3. **Integrasi Android**: Copy files ke project Android
4. **Testing**: Test model di aplikasi Android
5. **Production**: Deploy ke production environment

## 🤝 Support

Jika ada pertanyaan atau issue:

1. Cek log file untuk error details
2. Pastikan data Firestore sesuai struktur
3. Validasi Firebase credentials
4. Test dengan data sample terlebih dahulu
