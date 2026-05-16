"""
Data Collector — Auto-Record Mode
====================================
Otomatis menyimpan setiap bacaan sensor ke CSV tanpa perlu tekan Enter.

Cara pakai:
  1. Upload soil_fertility.ino ke ESP32, colok USB ke PC
  2. Jalankan: python src/data_collector.py
  3. Masukkan nama lokasi/sesi pengambilan data
  4. Script otomatis simpan setiap bacaan (~setiap 6 detik)
  5. Tekan Ctrl+C untuk ganti lokasi atau selesai

Output: data/real_data_raw.csv
"""

import serial
import serial.tools.list_ports
import csv, os, time, sys
from datetime import datetime

# ---- Konfigurasi ----
BAUD_RATE  = 115200
OUTPUT_DIR = r"c:\Users\DELL GAMING\Documents\Kuliah\Semester8\Sys_Tanah\data"
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "real_data_raw.csv")
CSV_HEADER = ["no", "timestamp", "lokasi", "Hum", "Temp", "N", "P", "K", "pH", "EC", "OC_est"]

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---- Deteksi port COM ----
def detect_port():
    ports = list(serial.tools.list_ports.comports())
    candidates = [p for p in ports if any(k in (p.description or "").lower()
                  for k in ["cp210", "ch340", "ftdi", "usb serial", "uart"])]
    if len(candidates) == 1:
        return candidates[0].device
    all_ports = candidates if candidates else ports
    if not all_ports:
        return None
    print("\nPort tersedia:")
    for i, p in enumerate(all_ports):
        print(f"  [{i}] {p.device}  —  {p.description}")
    idx = input("Pilih nomor port: ").strip()
    return all_ports[int(idx)].device if idx.isdigit() and int(idx) < len(all_ports) else all_ports[0].device

# ---- Parse baris CSV dari ESP32 ----
def parse_csv(line):
    line = line.strip()
    if not line.startswith("CSV,"):
        return None
    parts = line.split(",")
    if len(parts) != 9:
        return None
    try:
        return {
            "Hum":    float(parts[1]),
            "Temp":   float(parts[2]),
            "N":      float(parts[3]),
            "P":      float(parts[4]),
            "K":      float(parts[5]),
            "pH":     float(parts[6]),
            "EC":     int(float(parts[7])),
            "OC_est": float(parts[8]),
        }
    except ValueError:
        return None

# ---- Tampilkan data live ----
def show_live(data, lokasi, count):
    os.system("cls")
    print("╔══════════════════════════════════════════════╗")
    print("║         SOIL DATA COLLECTOR  — AUTO          ║")
    print("╠══════════════════════════════════════════════╣")
    print(f"║  Lokasi  : {lokasi:<34}║")
    print(f"║  Tersimpan: {count:>3} sampel                          ║")
    print("╠══════════════════════════════════════════════╣")
    print(f"║  Kelembaban  : {data['Hum']:>7.1f} %                    ║")
    print(f"║  Suhu        : {data['Temp']:>7.1f} C                    ║")
    print(f"║  N           : {data['N']:>7.1f} mg/kg                ║")
    print(f"║  P           : {data['P']:>7.1f} mg/kg                ║")
    print(f"║  K           : {data['K']:>7.1f} mg/kg                ║")
    print(f"║  pH          : {data['pH']:>7.2f}                      ║")
    print(f"║  EC          : {data['EC']:>7d} us/cm               ║")
    print(f"║  OC est      : {data['OC_est']:>7.2f} %                    ║")
    print("╠══════════════════════════════════════════════╣")
    print("║  Setiap bacaan tersimpan otomatis            ║")
    print("║  Ctrl+C = ganti lokasi / selesai             ║")
    print("╚══════════════════════════════════════════════╝")

# ============================================================
def main():
    os.system("cls")
    print("╔══════════════════════════════════════════════╗")
    print("║         SOIL DATA COLLECTOR  — AUTO          ║")
    print("╚══════════════════════════════════════════════╝")

    port = detect_port()
    if not port:
        print("ERROR: Tidak ada port serial ditemukan. Cek koneksi USB.")
        return

    print(f"\nMenghubungkan ke {port} @ {BAUD_RATE} baud...")
    try:
        ser = serial.Serial(port, BAUD_RATE, timeout=2)
    except serial.SerialException as e:
        print(f"ERROR: {e}")
        print("Pastikan Arduino IDE / Serial Monitor sudah ditutup!")
        return

    time.sleep(2)
    ser.reset_input_buffer()
    print("Terhubung!\n")

    # Hitung sampel yang sudah ada
    sample_count = 0
    file_exists  = os.path.exists(OUTPUT_CSV)
    if file_exists:
        with open(OUTPUT_CSV, "r", encoding="utf-8") as f:
            sample_count = max(0, sum(1 for _ in f) - 1)

    csvfile = open(OUTPUT_CSV, "a", newline="", encoding="utf-8")
    writer  = csv.DictWriter(csvfile, fieldnames=CSV_HEADER)
    if not file_exists:
        writer.writeheader()

    while True:
        # Tanya nama lokasi/toples
        os.system("cls")
        print("╔══════════════════════════════════════════════╗")
        print("║         SOIL DATA COLLECTOR  — AUTO          ║")
        print("╚══════════════════════════════════════════════╝")
        print(f"\n  Sampel tersimpan sejauh ini: {sample_count}")
        print("\n  Masukkan nama lokasi/toples untuk sesi ini.")
        print("  Contoh: Kebun A, Toples 1, Sawah Utara")
        lokasi = input("\n  Nama lokasi: ").strip()
        if not lokasi:
            lokasi = f"Sesi_{datetime.now().strftime('%H%M%S')}"

        print(f"\n  Memulai auto-record untuk lokasi: '{lokasi}'")
        print("  Tunggu data pertama...")

        sesi_count = 0
        try:
            while True:
                raw = ser.readline()
                if not raw:
                    continue
                try:
                    line = raw.decode("utf-8", errors="ignore")
                except Exception:
                    continue

                data = parse_csv(line)
                if data is None:
                    continue

                # Simpan otomatis
                sample_count += 1
                sesi_count   += 1
                ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                row = {"no": sample_count, "timestamp": ts, "lokasi": lokasi}
                row.update(data)
                writer.writerow(row)
                csvfile.flush()

                show_live(data, lokasi, sample_count)

        except KeyboardInterrupt:
            print(f"\n\n  Sesi '{lokasi}' selesai — {sesi_count} sampel direkam.")
            print(f"  Total dataset: {sample_count} sampel\n")
            cont = input("  [Enter] = ganti lokasi   |   [q + Enter] = selesai: ").strip().lower()
            if cont == "q":
                break

    ser.close()
    csvfile.close()
    print(f"\n✓ Data tersimpan di: {OUTPUT_CSV}")
    print(f"  Total: {sample_count} sampel")
    print(f"\nLangkah berikutnya:")
    print(f"  python src/auto_labeling.py    <- beri label otomatis")
    print(f"  python src/data_processing.py  <- preprocessing")

if __name__ == "__main__":
    main()
