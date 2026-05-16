"""
Data Collector — Auto-Record Mode (Supabase Edition)
======================================================
Otomatis menyimpan setiap bacaan sensor ke CSV lokal dan Supabase.

Cara pakai:
  1. Pastikan Anda sudah membuat file .env berisi SUPABASE_URL dan SUPABASE_KEY
  2. Upload soil_fertility.ino ke ESP32, colok USB ke PC
  3. Jalankan: python src/data_collector_supabase.py
  4. Masukkan nama lokasi/sesi pengambilan data
  5. Script otomatis simpan setiap bacaan (~setiap 6 detik)
  6. Tekan Ctrl+C untuk ganti lokasi atau selesai

Output: data/real_data_raw.csv dan Cloud Supabase
"""

import serial
import serial.tools.list_ports
import csv, os, time, sys
from datetime import datetime
from dotenv import load_dotenv

try:
    from supabase import create_client, Client
except ImportError:
    print("ERROR: Modul 'supabase' belum diinstal. Silakan jalankan 'pip install supabase python-dotenv'")
    sys.exit(1)

# ---- Load Environment Variables ----
load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("ERROR: SUPABASE_URL atau SUPABASE_KEY tidak ditemukan. Harap buat file .env di root folder.")
    sys.exit(1)

# Initialize Supabase client
supabase: Client = create_client(url, key)

# ---- Konfigurasi ----
BAUD_RATE  = 115200

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
def show_live(data, lokasi, count, db_status="OK"):
    os.system("cls")
    print("╔══════════════════════════════════════════════╗")
    print("║      SOIL DATA COLLECTOR  — SUPABASE         ║")
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
    print(f"║  Status DB : {db_status:<32}║")
    print("║  Setiap bacaan tersimpan otomatis            ║")
    print("║  Ctrl+C = ganti lokasi / selesai             ║")
    print("╚══════════════════════════════════════════════╝")

# ============================================================
def main():
    os.system("cls")
    print("╔══════════════════════════════════════════════╗")
    print("║      SOIL DATA COLLECTOR  — SUPABASE         ║")
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

    # Start sample count for this run
    sample_count = 0

    while True:
        # Tanya nama lokasi/toples
        os.system("cls")
        print("╔══════════════════════════════════════════════╗")
        print("║      SOIL DATA COLLECTOR  — SUPABASE         ║")
        print("╚══════════════════════════════════════════════╝")
        print(f"\n  Sampel lokal tersimpan sejauh ini: {sample_count}")
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

                sample_count += 1
                sesi_count   += 1

                # --- Simpan ke Supabase ---
                ts_iso = datetime.now().isoformat()
                db_status = "Tersimpan"
                try:
                    supabase_data = {
                        "timestamp": ts_iso,
                        "lokasi": lokasi,
                        "Hum": data["Hum"],
                        "Temp": data["Temp"],
                        "N": data["N"],
                        "P": data["P"],
                        "K": data["K"],
                        "pH": data["pH"],
                        "EC": data["EC"],
                        "OC_est": data["OC_est"]
                    }
                    response = supabase.table("soil_measurements").insert(supabase_data).execute()
                except Exception as e:
                    db_status = f"Gagal: {str(e)[:20]}"

                show_live(data, lokasi, sample_count, db_status)

        except KeyboardInterrupt:
            print(f"\n\n  Sesi '{lokasi}' selesai — {sesi_count} sampel direkam.")
            print(f"  Total dataset: {sample_count} sampel\n")
            cont = input("  [Enter] = ganti lokasi   |   [q + Enter] = selesai: ").strip().lower()
            if cont == "q":
                break

    ser.close()
    print(f"\n✓ Data selesai dikumpulkan.")
    print(f"  Total sampel sesi ini: {sample_count}")
    print(f"\nLangkah berikutnya:")
    print(f"  Cek Dashboard Supabase atau App Anda.")

if __name__ == "__main__":
    main()
