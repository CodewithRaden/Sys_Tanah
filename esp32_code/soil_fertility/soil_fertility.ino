/**
 * ============================================================
 * Soil Fertility Classification & Prediction System  v3.0
 * ============================================================
 * Hardware       : ESP32, MAX485, LCD I2C 16x4, Sensor NPK 7-in-1
 * AI Model       : Random Forest (Tuned, 5 Kelas) - micromlgen
 * Wiring MAX485  : DI(17), RO(16), DE(4), RE(5)
 * Wiring LCD     : SDA(21), SCL(22)
 * ============================================================
 * Sensor 7-in-1 Register Map (Modbus RTU, Addr 0x01, FC 0x03):
 *   Reg 0x0000 : Kelembaban Tanah (×10, %)
 *   Reg 0x0001 : Suhu Tanah      (×10, °C)
 *   Reg 0x0002 : EC              (us/cm)
 *   Reg 0x0003 : pH              (×10)
 *   Reg 0x0004 : N               (mg/kg)
 *   Reg 0x0005 : P               (mg/kg)
 *   Reg 0x0006 : K               (mg/kg)
 * ============================================================
 * Custom Characters (LCD CGRAM slots):
 *   0: Droplet   (Humidity)
 *   1: Leaf      (Fertility)
 *   2: Thermometer (Temperature)
 * ============================================================
 */

#include "rf_model.h"             // File model AI (5 kelas: Sangat Rendah-Sangat Tinggi)
#include <Wire.h>                // I2C
#include <LiquidCrystal_I2C.h>   // LCD I2C
#include <WiFi.h>                // WiFi Library
#include <ArduinoJson.h>         // JSON for ThingsBoard
#include <PubSubClient.h>        // MQTT for ThingsBoard
#include <time.h>                // NTP Time Sync
#include <sntp.h>
#include <SPIFFS.h>              // Persistent Offline Storage

// --- WiFi Configuration ---
const char* WIFI_SSID = "Itsme";
const char* WIFI_PASS = "1234567899";

// --- Konfigurasi Supabase dihapus: Kini diteruskan lewat ThingsBoard Rule Engine ---

// ============================
// THINGSBOARD CONFIG
// ============================
const char* TB_SERVER = "eu.thingsboard.cloud";  // Ganti dengan IP/domain ThingsBoard
const int   TB_PORT   = 1883;
const char* TB_TOKEN  = "4ossQPvhJirMfLB0NYVR";  // Access Token device

WiFiClient   espClient;
PubSubClient tbClient(espClient);

// FUNGSI UNTUK MENYIMPAN KE SPIFFS
void saveDataLocally(String data) {
  File file = SPIFFS.open("/unsent.txt", FILE_APPEND);
  if (file) {
    file.println(data);
    file.close();
  } else {
    Serial.println("[SPIFFS] Gagal membuka file untuk menulis.");
  }
}

// FUNGSI UNTUK MENGIRIM DATA TERSIMPAN VIA MQTT
void syncUnsentData() {
  if (!SPIFFS.exists("/unsent.txt")) return;

  File file = SPIFFS.open("/unsent.txt", FILE_READ);
  if (!file || file.size() == 0) {
    if (file) file.close();
    SPIFFS.remove("/unsent.txt");
    return;
  }

  Serial.println("[Sync] Membaca data offline dari SPIFFS...");
  String allData = "";
  while (file.available()) {
    allData += file.readStringUntil('\n') + "\n";
  }
  file.close();
  
  SPIFFS.remove("/unsent.txt"); // Hapus file lama, nanti ditulis ulang kalau ada yang gagal

  int pos = 0;
  int successCount = 0;
  int failCount = 0;
  String rewriteData = "";

  while (pos < allData.length()) {
    int endLine = allData.indexOf('\n', pos);
    if (endLine == -1) break;
    String line = allData.substring(pos, endLine);
    pos = endLine + 1;
    line.trim();
    if (line.length() == 0) continue;

    StaticJsonDocument<512> lineDoc;
    DeserializationError err = deserializeJson(lineDoc, line);
    if (!err) {
      if (tbClient.connected() && lineDoc.containsKey("epoch_ms")) {
        StaticJsonDocument<512> hDoc;
        hDoc["ts"] = lineDoc["epoch_ms"];
        JsonObject vals = hDoc.createNestedObject("values");
        // Karena di SPIFFS kita simpan pakai huruf kecil (sesuai keys MQTT), kita ambil huruf kecil:
        vals["humidity"]    = lineDoc["humidity"];
        vals["temperature"] = lineDoc["temperature"];
        vals["n"]           = lineDoc["n"];
        vals["p"]           = lineDoc["p"];
        vals["k"]           = lineDoc["k"];
        vals["ph"]          = lineDoc["ph"];
        vals["ec"]          = lineDoc["ec"];
        vals["ai_label"]    = lineDoc["ai_label"];
        vals["recommendation"] = lineDoc["recommendation"];
        
        String hPayload;
        serializeJson(hDoc, hPayload);
        if (tbClient.publish("v1/devices/me/telemetry", hPayload.c_str())) {
          successCount++;
          delay(50); // Kasih nafas untuk jaringan
        } else {
          failCount++;
          rewriteData += line + "\n"; // Kembalikan ke memori jika gagal kirim
        }
      } else {
        failCount++;
        rewriteData += line + "\n";
      }
    }
  }

  // Tulis ulang data yang gagal dikirim
  if (rewriteData.length() > 0) {
    File rewriteFile = SPIFFS.open("/unsent.txt", FILE_WRITE);
    if (rewriteFile) {
      rewriteFile.print(rewriteData);
      rewriteFile.close();
    }
  }

  if (successCount > 0 || failCount > 0) {
    Serial.println("--- Hasil Sinkronisasi Offline ---");
    Serial.printf("Sukses terkirim : %d\n", successCount);
    Serial.printf("Gagal / Sisa    : %d\n", failCount);
    Serial.println("----------------------------------");
  }
}

// --- Pin MAX485 ---
#define DE_PIN  4
#define RE_PIN  5
#define RX2_PIN 16
#define TX2_PIN 17

// --- Modbus request: baca 7 register mulai 0x0000 ---
const byte soilQuery[] = {0x01, 0x03, 0x00, 0x00, 0x00, 0x07, 0x04, 0x08};
byte values[19];  // 3 header + 14 data + 2 CRC

// --- LCD 20x4 ---
LiquidCrystal_I2C lcd(0x27, 20, 4);

// ============================================================
//  CUSTOM CHARACTERS — 3 ikon (5×8 pixel)
// ============================================================

// Slot 0: Water Droplet (kelembaban)
byte iconDrop[8] = {
  0b00100,
  0b00100,
  0b01110,
  0b01110,
  0b11111,
  0b11111,
  0b11111,
  0b01110
};

// Slot 1: Leaf (kesuburan/tanaman)
byte iconLeaf[8] = {
  0b00010,
  0b00110,
  0b01110,
  0b11110,
  0b01111,
  0b00111,
  0b00110,
  0b01100
};

// Slot 2: Thermometer (suhu)
byte iconThermo[8] = {
  0b00100,
  0b01010,
  0b01010,
  0b01010,
  0b01110,
  0b11111,
  0b11111,
  0b01110
};

// Custom char index aliases
#define ICON_DROP   0
#define ICON_LEAF   1
#define ICON_THERMO 2

// --- Profil Ideal — dipakai untuk rekomendasi pupuk (bukan prediksi model) ---
// Model baru (rf_model.h) menggunakan raw features tanpa StandardScaler
// Features: N, P, K, pH, EC (5 fitur)
const float IDEAL_N  = 200.0f;   // mg/kg
const float IDEAL_P  = 300.0f;   // mg/kg
const float IDEAL_K  = 500.0f;   // mg/kg
const float IDEAL_PH = 6.8f;     // pH optimal
const float IDEAL_EC = 700.0f;   // us/cm

#define IDX_N  0
#define IDX_P  1
#define IDX_K  2
#define IDX_PH 3
#define IDX_EC 4

Eloquent::ML::Port::RandomForest classifier;
// Model rf_model.h menggunakan raw values (tanpa StandardScaler)

// ============================================================
//  LCD HELPER FUNCTIONS
// ============================================================

// Bersihkan lalu tulis teks di baris tertentu
void lcdPrint(uint8_t row, const char* text) {
  lcd.setCursor(0, row);
  lcd.print("                    ");   // bersihkan 20 kolom
  lcd.setCursor(0, row);
  lcd.print(text);
}

// Tulis custom character di posisi tertentu
void lcdIcon(uint8_t col, uint8_t row, uint8_t charIdx) {
  lcd.setCursor(col, row);
  lcd.write(byte(charIdx));
}

// Tulis teks rata tengah di baris tertentu
void lcdCenter(uint8_t row, const char* text) {
  int len = strlen(text);
  int pad = (20 - len) / 2;
  if (pad < 0) pad = 0;
  lcd.setCursor(0, row);
  lcd.print("                    ");
  lcd.setCursor(pad, row);
  lcd.print(text);
}

// Tampilkan rekomendasi cycling di baris 3
void showRecom(const char* isi) {
  lcdPrint(3, isi);
  delay(500);
}

// ============================================================
//  SPLASH SCREEN — Animasi saat boot
// ============================================================
void splashScreen() {
  lcd.clear();

  // Baris 0: leaf + judul
  lcdCenter(0, "  Soil AI v3.0  ");
  lcdIcon(2, 0, ICON_LEAF);
  lcdIcon(17, 0, ICON_LEAF);

  // Baris 1 & 2: subtitle (rata tengah)
  lcdCenter(1, "Smart Farming");
  lcdCenter(2, "System");

  // Baris 3: animasi loading bar
  delay(400);
  lcd.setCursor(0, 3);
  lcd.print("[");
  lcd.setCursor(19, 3);
  lcd.print("]");
  for (int i = 1; i <= 18; i++) {
    lcd.setCursor(i, 3);
    lcd.write(0xFF);   // blok penuh bawaan LCD
    delay(90);
  }

  delay(400);

  // Flash "READY!"
  lcd.clear();
  lcdCenter(1, "  READY!  ");
  lcdIcon(5, 1, ICON_LEAF);
  lcdIcon(14, 1, ICON_LEAF);
  delay(1200);

  lcd.clear();
}

// ============================================================
//  Fungsi utama tampil hasil (Serial + LCD)
// ============================================================
void showResult(int pred,
                float hum, float temp,
                float n,   float p, float k,
                float ph,  float ec,
                String &outLabel, String &outRecom) {
  char r[21];   // buffer baris LCD (20 char + null)

  // ========================================================
  // SERIAL MONITOR — semua data sejajar
  // ========================================================
  Serial.println("====================================");
  Serial.println("   HASIL ANALISIS KUALITAS TANAH   ");
  Serial.println("====================================");
  Serial.printf(" Kelembaban : %5.1f %%\n",   hum);
  Serial.printf(" Suhu       : %5.1f degC\n", temp);
  Serial.println("------------------------------------");
  Serial.printf(" N  : %6.0f mg/kg\n", n);
  Serial.printf(" P  : %6.0f mg/kg\n", p);
  Serial.printf(" K  : %6.0f mg/kg\n", k);
  Serial.printf(" pH : %6.1f\n",        ph);
  Serial.printf(" EC : %6d us/cm\n",    (int)ec);
  Serial.println("====================================");

  // ========================================================
  // HALAMAN 1 — Data Sensor (10 detik)
  //
  //   Baris 0: "💧XX.X%  🌡XX.XC "  ← Hum + Suhu + ikon
  //   Baris 1: "N:XXX P:XX K:XXX "  ← NPK
  //   Baris 2: "pH:X.XX  EC:XXXX "  ← pH + EC
  //   Baris 3: kosong
  // ========================================================
  lcd.clear();

  // -- Baris 0: Kelembaban & Suhu --
  lcd.setCursor(0, 0);
  lcd.write(byte(ICON_DROP));
  snprintf(r, sizeof(r), " %.1f%%", hum);
  lcd.setCursor(1, 0);
  lcd.print(r);

  int nextCol = 1 + strlen(r);
  for (int i = nextCol; i < 11; i++) {
    lcd.setCursor(i, 0);
    lcd.print(" ");
  }
  lcd.setCursor(11, 0);
  lcd.write(byte(ICON_THERMO));
  snprintf(r, sizeof(r), " %.1fC", temp);
  lcd.setCursor(12, 0);
  lcd.print(r);

  // -- Baris 1: N, P, K --
  int ni = min((int)n, 999);
  int pi = min((int)p, 999);
  int ki = min((int)k, 999);
  snprintf(r, sizeof(r), "N:%-3d  P:%-3d  K:%-3d", ni, pi, ki);
  lcdPrint(1, r);

  // -- Baris 3: pH dan EC --
  snprintf(r, sizeof(r), "pH: %.1f   EC: %4d", ph, (int)ec);
  lcdPrint(2, r);

  // -- Baris 3: kosong / siap rekomendasi --
  lcdPrint(3, "");

  delay(10000);

  // ========================================================
  // HALAMAN 2 — Hasil AI (5 Kelas) + Rekomendasi
  //
  //   Kelas 0: Sangat Rendah
  //   Kelas 1: Rendah
  //   Kelas 2: Sedang
  //   Kelas 3: Tinggi
  //   Kelas 4: Sangat Tinggi
  // ========================================================
  lcd.clear();

  // -- Baris 0: Header dekoratif --
  lcdCenter(0, "===  HASIL AI  ===");
  lcdIcon(3, 0, ICON_LEAF);
  lcdIcon(16, 0, ICON_LEAF);

  outRecom = "";

  // ---- Tampilkan label kesuburan di Baris 1 ----
  // LCD 20x4: lcdCenter otomatis menghitung padding
  // "SANGAT RENDAH" (13 chr) -> pad=3, teks col 3-15, icon di col 1 & 17
  // "RENDAH"        ( 6 chr) -> pad=7, teks col 7-12, icon di col 5 & 14
  // "SEDANG"        ( 6 chr) -> pad=7, teks col 7-12, icon di col 5 & 14
  // "TINGGI"        ( 6 chr) -> pad=7, teks col 7-12, icon di col 5 & 14
  // "SANGAT TINGGI" (13 chr) -> pad=3, teks col 3-15, icon di col 1 & 17
  switch (pred) {
    case 0:  // Sangat Rendah — pad=3, teks col 3-15
      outLabel = "Sangat Rendah";
      lcdCenter(1, "SANGAT RENDAH");
      lcdIcon(1, 1, ICON_LEAF);
      lcdIcon(17, 1, ICON_LEAF);
      Serial.println(" Status: SANGAT RENDAH");
      break;
    case 1:  // Rendah — pad=7, teks col 7-12
      outLabel = "Rendah";
      lcdCenter(1, "RENDAH");
      lcdIcon(5, 1, ICON_LEAF);
      lcdIcon(14, 1, ICON_LEAF);
      Serial.println(" Status: RENDAH");
      break;
    case 2:  // Sedang — pad=7, teks col 7-12
      outLabel = "Sedang";
      lcdCenter(1, "SEDANG");
      lcdIcon(5, 1, ICON_LEAF);
      lcdIcon(14, 1, ICON_LEAF);
      Serial.println(" Status: SEDANG");
      break;
    case 3:  // Tinggi — pad=7, teks col 7-12
      outLabel = "Tinggi";
      lcdCenter(1, "TINGGI");
      lcdIcon(5, 1, ICON_LEAF);
      lcdIcon(14, 1, ICON_LEAF);
      Serial.println(" Status: TINGGI");
      break;
    case 4:  // Sangat Tinggi — pad=3, teks col 3-15
      outLabel = "Sangat Tinggi";
      lcdCenter(1, "SANGAT TINGGI");
      lcdIcon(1, 1, ICON_LEAF);
      lcdIcon(17, 1, ICON_LEAF);
      Serial.println(" Status: SANGAT TINGGI");
      break;
    default:
      outLabel = "Unknown";
      lcdCenter(1, "UNKNOWN");
      Serial.println(" Status: UNKNOWN");
      break;
  }

  lcdPrint(2, "Rekomendasi:        ");
  lcdPrint(3, "                    ");
  delay(500);

  bool hasRecom = false;

  // ---- Rekomendasi Kelas 4 (Sangat Tinggi) ----
  if (pred == 4) {
    outRecom = "Pertahankan, kurangi pupuk kimia.";
    showRecom("Pertahankan!    ");
    Serial.println(" Tindakan: Pertahankan kondisi saat ini.");
    delay(1000);
  } else {
    // ---- Rekomendasi berbasis defisiensi nutrisi ----
    if (n < IDEAL_N * 0.8f) {
      Serial.printf(" - N Rendah (%.0f mg/kg) -> Tambah Urea\n", n);
      showRecom("+Urea / Kompos  ");
      outRecom += "Tambah Urea, ";
      hasRecom = true;
    }
    if (p < IDEAL_P * 0.8f) {
      Serial.printf(" - P Rendah (%.0f mg/kg) -> Tambah SP-36\n", p);
      showRecom("+SP-36/Rock Phos");
      outRecom += "Tambah SP-36, ";
      hasRecom = true;
    }
    if (k < IDEAL_K * 0.8f) {
      Serial.printf(" - K Rendah (%.0f mg/kg) -> Tambah KCl\n", k);
      showRecom("+KCl / Abu Kayu ");
      outRecom += "Tambah KCl, ";
      hasRecom = true;
    }
    if (ph < 5.5f) {
      Serial.printf(" - pH Asam (%.2f) -> Tambah Kapur Dolomit\n", ph);
      showRecom("+Kapur Dolomit  ");
      outRecom += "Tambah Kapur Dolomit, ";
      hasRecom = true;
    } else if (ph > 7.5f) {
      Serial.printf(" - pH Basa (%.2f) -> Tambah Belerang\n", ph);
      showRecom("+Belerang/Sulfur");
      outRecom += "Tambah Belerang, ";
      hasRecom = true;
    }
    if (!hasRecom) {
      showRecom("  Kondisi Baik! ");
      outRecom = "Kondisi Baik!";
    } else {
      outRecom.remove(outRecom.length() - 2); // Hilangkan koma dan spasi terakhir
    }
  }

  Serial.println("====================================\n");
}

// ============================================================
//  THINGSBOARD MQTT — Reconnect jika putus
// ============================================================
void tbReconnect() {
  int retries = 0;
  while (!tbClient.connected() && retries < 3) {
    Serial.print("[MQTT] Connecting to ThingsBoard...");
    if (tbClient.connect("ESP32_Soil_AI", TB_TOKEN, NULL)) {
      Serial.println(" CONNECTED!");
    } else {
      Serial.printf(" FAILED (rc=%d), retry %d/3\n", tbClient.state(), retries + 1);
      retries++;
      delay(2000);
    }
  }
}

// ============================================================
void setup() {
  Serial.begin(115200);
  Serial2.begin(4800, SERIAL_8N1, RX2_PIN, TX2_PIN);

  pinMode(DE_PIN, OUTPUT);
  pinMode(RE_PIN, OUTPUT);
  digitalWrite(DE_PIN, LOW);
  digitalWrite(RE_PIN, LOW);

  // --- Inisialisasi SPIFFS ---
  if (!SPIFFS.begin(true)) {
    Serial.println("SPIFFS Mount Failed! Data offline tidak bisa disimpan.");
  } else {
    Serial.println("SPIFFS OK.");
  }

  // --- Inisialisasi LCD + custom characters ---
  lcd.begin();
  lcd.backlight();
  lcd.createChar(ICON_DROP,   iconDrop);
  lcd.createChar(ICON_LEAF,   iconLeaf);
  lcd.createChar(ICON_THERMO, iconThermo);

  // --- Splash screen animasi ---
  splashScreen();

  // --- Connect WiFi ---
  lcd.clear();
  lcdCenter(0, "Menghubungkan");
  lcdCenter(1, "ke WiFi...");
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  int attempt = 0;
  while (WiFi.status() != WL_CONNECTED && attempt < 20) {
    delay(500);
    Serial.print(".");
    attempt++;
  }
  if (WiFi.status() == WL_CONNECTED) {
    lcdPrint(2, "WiFi Terhubung!");
    Serial.println("\nWiFi Connected!");
    tbClient.setServer(TB_SERVER, TB_PORT);  // Setup MQTT ThingsBoard
    configTime(7 * 3600, 0, "pool.ntp.org", "time.nist.gov"); // Sync jam ke WIB (UTC+7)
    
    // Sync data yang tertahan selama alat mati
    syncUnsentData();
  } else {
    lcdPrint(2, "Gagal Konek WiFi");
    Serial.println("\nWiFi Failed!");
  }
  delay(2000);
  lcd.clear();

  Serial.println("============================================");
  Serial.println("  Soil AI System v3.0 - Smart Farming");
  Serial.println("  Model: RF 5 Kelas (Sangat Rendah - Sangat Tinggi)");
  Serial.println("============================================");
  Serial.println("Sistem Prediksi Tanah AI Siap!\n");
}

// ============================================================
void loop() {
  // --- WIFI AUTO-RECONNECT (Non-Blocking) ---
  if (WiFi.status() != WL_CONNECTED) {
    static unsigned long lastWiFiCheck = 0;
    if (millis() - lastWiFiCheck >= 10000) { // Coba konek ulang tiap 10 detik
      Serial.println("[Wi-Fi] Terputus! Mencoba menyambung kembali...");
      WiFi.disconnect();
      WiFi.reconnect();
      lastWiFiCheck = millis();
    }
  }

  // --- MQTT KEEPALIVE ThingsBoard ---
  if (WiFi.status() == WL_CONNECTED) {
    if (!tbClient.connected()) tbReconnect();
    tbClient.loop(); // wajib ada agar koneksi MQTT tidak timeout
  }

  // 1. Kirim request Modbus ke sensor
  digitalWrite(DE_PIN, HIGH);
  digitalWrite(RE_PIN, HIGH);
  delay(10);
  Serial2.write(soilQuery, sizeof(soilQuery));
  Serial2.flush();

  // 2. Kembali ke mode receive
  digitalWrite(DE_PIN, LOW);
  digitalWrite(RE_PIN, LOW);
  delay(200);

  // 3. Baca balasan (19 byte)
  int index = 0;
  while (Serial2.available() > 0 && index < 19) {
    values[index++] = Serial2.read();
  }

  // 4. Validasi & parse
  if (index == 19 && values[0] == 0x01 && values[1] == 0x03 && values[2] == 0x0E) {

    float hum  = (values[3]  << 8 | values[4])  / 10.0f;
    float temp = (values[5]  << 8 | values[6])  / 10.0f;
    float ec   = (float)(values[7]  << 8 | values[8]);
    float ph   = (values[9]  << 8 | values[10]) / 10.0f;
    float n    = (float)(values[11] << 8 | values[12]);
    float p    = (float)(values[13] << 8 | values[14]);
    float k    = (float)(values[15] << 8 | values[16]);

    // --- Sanity Check: N=0, P=0, K=0, EC=0 → sensor belum baca / tidak valid ---
    // Nilai NPK dan EC semuanya 0 tidak mungkin terjadi di tanah nyata.
    // Biasanya terjadi di pembacaan pertama atau saat koneksi RS485 belum stabil.
    if (n == 0 && p == 0 && k == 0 && ec == 0) {
      Serial.printf("[WARN] Data tidak valid — N:%.0f P:%.0f K:%.0f EC:%.0f pH:%.1f | Skip AI.\n",
                    n, p, k, ec, ph);

      lcd.clear();

      // Baris 0: "  [DROP] SENSOR ERROR [DROP]  "
      // "SENSOR  ERROR" = 13 char → pad=3 (col 3-15), ikon di col 1 & 18
      lcdCenter(0, "SENSOR  ERROR");
      lcdIcon(1, 0, ICON_DROP);
      lcdIcon(18, 0, ICON_DROP);

      // Baris 1: status singkat
      // "Data Tidak Valid" = 16 char → pad=2
      lcdCenter(1, "Data Tidak Valid");

      // Baris 2: nilai yang bermasalah
      // "N=P=K=EC = 0" = 13 char → pad=3
      lcdCenter(2, "N=P=K=EC = 0");

      // Baris 3: countdown animasi 3 detik
      for (int c = 3; c > 0; c--) {
        char cbuf[21];
        // "Coba ulang: 3 detik" = 19 char → pad=0
        snprintf(cbuf, sizeof(cbuf), "Coba ulang: %d detik", c);
        lcdCenter(3, cbuf);
        delay(1000);
      }
      return; // skip prediksi & pengiriman data
    }

    // Model rf_model.h: 5 fitur RAW (tanpa scaling) — N, P, K, pH, EC
    float features[5];
    features[IDX_N]  = n;
    features[IDX_P]  = p;
    features[IDX_K]  = k;
    features[IDX_PH] = ph;
    features[IDX_EC] = ec;

    unsigned long start_time = micros();
    int prediction = classifier.predict(features);
    unsigned long latency = micros() - start_time;
    float latency_sec = latency / 1000000.0f;
    Serial.printf("\n[AI Latency: %.6f seconds]\n", latency_sec);
    Serial.printf("[AI Class: %d = %s]\n", prediction, classifier.idxToLabel(prediction));

    String aiLabel = "";
    String aiRecom = "";
    showResult(prediction, hum, temp, n, p, k, ph, ec, aiLabel, aiRecom);

    // --- Persiapkan Payload JSON Utama ---
    StaticJsonDocument<512> doc;
    doc["humidity"]    = hum;
    doc["temperature"] = temp;
    doc["n"]           = n;
    doc["p"]           = p;
    doc["k"]           = k;
    doc["ph"]          = ph;
    doc["ec"]          = (int)ec;
    doc["ai_label"]    = aiLabel;
    doc["recommendation"] = aiRecom;

    bool sentOnline = false;

    // --- 1. Coba Kirim Telemetri ke ThingsBoard via MQTT ---
    if (tbClient.connected()) {
      String mqttPayload;
      serializeJson(doc, mqttPayload);

      unsigned long start_mqtt = millis();
      bool success = tbClient.publish("v1/devices/me/telemetry", mqttPayload.c_str());
      unsigned long end_mqtt = millis();

      if (success) {
        Serial.printf("[MQTT] Data terkirim ke ThingsBoard. (Latensi: %lu ms)\n", (end_mqtt - start_mqtt));
        sentOnline = true;
        
        // Coba sinkronisasi sisa data offline (jika ada) karena koneksi bagus
        syncUnsentData();
      } else {
        Serial.println("[MQTT] Gagal kirim ke ThingsBoard.");
      }
    } else {
      Serial.println("[MQTT] Tidak terhubung ke ThingsBoard.");
    }

    // --- 2. Jika Gagal Kirim Online (Offline), Simpan ke Memori SPIFFS ---
    if (!sentOnline) {
      // Sisipkan jam JIKA sudah punya jam yang valid dari NTP
      time_t now;
      time(&now);
      if (now > 1600000000) {
        doc["epoch_ms"]  = (unsigned long long)now * 1000ULL;
      }
      
      String currentData;
      serializeJson(doc, currentData);
      saveDataLocally(currentData);
      Serial.println("[Offline] Data aman, ditampung sementara di memori SPIFFS.");
    }

  } else {
    // ========================================================
    // HALAMAN ERROR — Clean layout
    // ========================================================
    char buf[17];
    Serial.printf("Gagal baca sensor. Diterima %d byte.\n", index);

    lcd.clear();
    lcdCenter(0, "!! SENSOR ERROR !!");
    snprintf(buf, sizeof(buf), "Recv: %2d/19 byte", index);
    lcdCenter(1, buf);
    lcdCenter(2, "Cek kabel RS485");
    lcdCenter(3, "atau baudrate");
    delay(3000);
  }

  delay(1000);
}