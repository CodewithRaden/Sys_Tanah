/**
 * ============================================================
 * Soil Fertility Classification & Prediction System  v2.0
 * ============================================================
 * Hardware       : ESP32, MAX485, LCD I2C 16x4, Sensor NPK 7-in-1
 * AI Model       : Random Forest (Tuned) - micromlgen
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

#include "model.h"               // File model AI
#include <Wire.h>                // I2C
#include <LiquidCrystal_I2C.h>   // LCD I2C
#include <WiFi.h>                // WiFi Library
#include <HTTPClient.h>          // HTTP Client
#include <WiFiClientSecure.h>    // HTTPS
#include <ArduinoJson.h>         // JSON for Supabase
#include <time.h>                // NTP Time Sync
#include <sntp.h>

#define MAX_OFFLINE_RECORDS 60

struct SensorRecord {
  float hum;
  float temp;
  float n;
  float p;
  float k;
  float ph;
  float ec;
  float oc;
  char label[20];
  char recom[150];
  time_t timestamp;
};

SensorRecord offlineBuffer[MAX_OFFLINE_RECORDS];
int offlineCount = 0;

void addRecord(float hum, float temp, float n, float p, float k, float ph, float ec, float oc, const String &label, const String &recom) {
  time_t now;
  time(&now);
  
  if (offlineCount >= MAX_OFFLINE_RECORDS) {
    // Geser array ke kiri untuk membuang data tertua
    for (int i = 1; i < MAX_OFFLINE_RECORDS; i++) {
      offlineBuffer[i - 1] = offlineBuffer[i];
    }
    offlineCount = MAX_OFFLINE_RECORDS - 1;
  }
  
  offlineBuffer[offlineCount].hum = hum;
  offlineBuffer[offlineCount].temp = temp;
  offlineBuffer[offlineCount].n = n;
  offlineBuffer[offlineCount].p = p;
  offlineBuffer[offlineCount].k = k;
  offlineBuffer[offlineCount].ph = ph;
  offlineBuffer[offlineCount].ec = ec;
  offlineBuffer[offlineCount].oc = oc;
  
  strncpy(offlineBuffer[offlineCount].label, label.c_str(), sizeof(offlineBuffer[offlineCount].label) - 1);
  offlineBuffer[offlineCount].label[sizeof(offlineBuffer[offlineCount].label) - 1] = '\0';
  
  strncpy(offlineBuffer[offlineCount].recom, recom.c_str(), sizeof(offlineBuffer[offlineCount].recom) - 1);
  offlineBuffer[offlineCount].recom[sizeof(offlineBuffer[offlineCount].recom) - 1] = '\0';
  
  offlineBuffer[offlineCount].timestamp = now;
  offlineCount++;
}

// --- WiFi Configuration ---
const char* WIFI_SSID = "Raden_2nd";
const char* WIFI_PASS = "onlyraden123";

// --- Supabase Configuration ---
const char* SUPABASE_URL = "https://zngqajfkegxhwwjoocka.supabase.co/rest/v1/soil_measurements";
const char* SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpuZ3FhamZrZWd4aHd3am9vY2thIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg2NjQwODUsImV4cCI6MjA5NDI0MDA4NX0.ShtqLC3CIxx2m3TVNbcZX5VftLFLbJCSkZAfr8wCNrE";

unsigned long lastSupabaseUpdate = 0;
const unsigned long SUPABASE_INTERVAL = 0; // 0 detik (kirim terus)

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

// --- Scaler & Profil Ideal (sesuai model AI) ---
// TODO: Setelah retrain dengan data sensor, update MEAN & SCALE dari
//       src/processed_data/scaler_params.csv yang baru.
const float MEAN[6]  = {146.77f, 11.00f, 557.63f, 7.07f, 0.60f, 0.69f};
const float SCALE[6] = { 51.48f,  4.17f, 187.76f, 0.66f, 0.24f, 0.31f};

// Profil ideal — diselaraskan dengan range sensor NPK 7-in-1
// Dipakai untuk rekomendasi pupuk (bukan untuk prediksi model)
const float IDEAL[6] = {200.0f, 300.0f, 500.0f, 6.8f, 700.0f, 0.80f};

// --- Koefisien Estimasi OC (Pedotransfer C/N + pH) ---
// Sumber: regresi dari dataset1.csv (src/oc_estimator.py)
// Formula: OC = OC_A0 + OC_AN*(N/10000) + OC_APH*(7.0-pH)
const float OC_A0   =  0.550886f; // intercept
const float OC_AN   =  3.405174f; // koef N  (input dalam persen: N_mg/10000)
const float OC_APH  =  0.033136f; // koef (7 - pH)
const float OC_CMIN =  0.1000f;   // batas bawah clamp
const float OC_CMAX =  3.0000f;   // batas atas clamp (wajar untuk lahan mineral)

#define IDX_N  0
#define IDX_P  1
#define IDX_K  2
#define IDX_PH 3
#define IDX_EC 4
#define IDX_OC 5

Eloquent::ML::Port::RandomForest classifier;

// ---- Standard scaling ----
float scaleFeature(float value, int idx) {
  return (value - MEAN[idx]) / SCALE[idx];
}

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
  lcdCenter(0, "  Soil AI v2.0  ");
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
                float ph,  float ec, float oc,
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
  Serial.printf(" N  : %6.1f mg/kg\n", n);
  Serial.printf(" P  : %6.1f mg/kg\n", p);
  Serial.printf(" K  : %6.1f mg/kg\n", k);
  Serial.printf(" pH : %6.2f\n",        ph);
  Serial.printf(" EC : %6d us/cm\n",    (int)ec);
  Serial.printf(" OC : %6.2f %%  (est)\n", oc);
  Serial.println("====================================");


  // ========================================================
  // HALAMAN 1 — Data Sensor (5 detik)
  //
  //   Baris 0: "💧XX.X%  🌡XX.XC "  ← Hum + Suhu + ikon
  //   Baris 1: "N:XXX P:XX K:XXX "  ← NPK
  //   Baris 2: "pH:X.XX  EC:XXXX "  ← pH + EC
  //   Baris 3: "OC est:  X.XX %  "  ← OC estimasi
  // ========================================================
  lcd.clear();

  // -- Baris 0: Kelembaban & Suhu --
  lcd.setCursor(0, 0);
  lcd.write(byte(ICON_DROP));                 // 💧 col 0
  snprintf(r, sizeof(r), " %.1f%%", hum);
  lcd.setCursor(1, 0);
  lcd.print(r);

  int nextCol = 1 + strlen(r);
  // Isi spasi sampai col 11
  for (int i = nextCol; i < 11; i++) {
    lcd.setCursor(i, 0);
    lcd.print(" ");
  }
  lcd.setCursor(11, 0);
  lcd.write(byte(ICON_THERMO));               // 🌡 col 11
  snprintf(r, sizeof(r), " %.1fC", temp);
  lcd.setCursor(12, 0);
  lcd.print(r);

  // -- Baris 1: N, P, K --
  int ni = min((int)n, 999);
  int pi = min((int)p, 999);
  int ki = min((int)k, 999);
  snprintf(r, sizeof(r), "N:%-3d  P:%-3d  K:%-3d", ni, pi, ki);
  lcdPrint(1, r);

  // -- Baris 2: pH dan EC --
  snprintf(r, sizeof(r), "pH: %.2f   EC: %4d", ph, (int)ec);
  lcdPrint(2, r);

  // -- Baris 3: OC estimasi --
  snprintf(r, sizeof(r), "OC est:  %5.2f %%", oc);
  lcdPrint(3, r);

  delay(1000); // Dipercepat untuk koleksi data (awalnya 10 detik)

  // ========================================================
  // HALAMAN 2 — Hasil AI + Rekomendasi
  //
  //   Baris 0: "==🌿 HASIL AI 🌿=="  ← header dekoratif
  //   Baris 1: status kesuburan
  //   Baris 2: "Rekomendasi:    "
  //   Baris 3: isi rekomendasi (cycling tiap 2.5 detik)
  // ========================================================
  lcd.clear();

  // -- Baris 0: Header dekoratif --
  lcdCenter(0, "===  HASIL AI  ===");
  lcdIcon(3, 0, ICON_LEAF);
  lcdIcon(16, 0, ICON_LEAF);

  outRecom = "";

  if (pred == 2) {
    // ---- SANGAT SUBUR ----
    outLabel = "Sangat Subur";
    outRecom = "Pertahankan kondisi saat ini.";

    lcdCenter(1, "  SANGAT SUBUR  ");
    lcdIcon(2, 1, ICON_LEAF);
    lcdIcon(17, 1, ICON_LEAF);

    lcdCenter(2, "Status: Optimal");
    lcdCenter(3, "Pertahankan!");

    Serial.println(" Status  : SANGAT SUBUR");
    Serial.println(" Tindakan: Pertahankan kondisi saat ini.");
    delay(1000);

  } else {
    // ---- SUBUR atau KURANG SUBUR ----
    if (pred == 1) {
      outLabel = "Subur";
      lcdCenter(1, "     SUBUR      ");
      lcdIcon(3, 1, ICON_LEAF);
      lcdIcon(16, 1, ICON_LEAF);
      Serial.println(" Status: SUBUR");
    } else {
      outLabel = "Kurang Subur";
      lcdCenter(1, "  KURANG SUBUR  ");
      lcdIcon(1, 1, ICON_LEAF);
      lcdIcon(18, 1, ICON_LEAF);
      Serial.println(" Status: KURANG SUBUR");
    }

    lcdPrint(2, "Rekomendasi:        ");
    lcdPrint(3, "                    ");
    delay(500);

    bool hasRecom = false;

    if (n < IDEAL[IDX_N] * 0.8f) {
      Serial.printf(" - N Rendah (%.0f mg/kg) -> Tambah Urea\n", n);
      showRecom("+Urea / Kompos  ");
      outRecom += "Tambah Urea, ";
      hasRecom = true;
    }
    if (p < IDEAL[IDX_P] * 0.8f) {
      Serial.printf(" - P Rendah (%.0f mg/kg) -> Tambah SP-36\n", p);
      showRecom("+SP-36/Rock Phos");
      outRecom += "Tambah SP-36, ";
      hasRecom = true;
    }
    if (k < IDEAL[IDX_K] * 0.8f) {
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
    if (oc < 0.5f) {
      Serial.println(" - C-Organik Rendah -> Tambah Pupuk Kandang");
      showRecom("+Pupuk Kandang  ");
      outRecom += "Tambah Pupuk Kandang, ";
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
void setup() {
  Serial.begin(115200);
  Serial2.begin(4800, SERIAL_8N1, RX2_PIN, TX2_PIN);

  pinMode(DE_PIN, OUTPUT);
  pinMode(RE_PIN, OUTPUT);
  digitalWrite(DE_PIN, LOW);
  digitalWrite(RE_PIN, LOW);

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
    configTime(7 * 3600, 0, "pool.ntp.org", "time.nist.gov"); // Sync jam ke WIB (UTC+7)
  } else {
    lcdPrint(2, "Gagal Konek WiFi");
    Serial.println("\nWiFi Failed!");
  }
  delay(2000);
  lcd.clear();

  Serial.println("============================================");
  Serial.println("  Soil AI System v2.0 - Smart Farming");
  Serial.println("============================================");
  Serial.println("Sistem Prediksi Tanah AI Siap!\n");
}

// ============================================================
void loop() {
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
    // Estimasi OC via Pedotransfer Function (C/N ratio + faktor pH)
    // OC(%) = a0 + a_N*(N%/100) + a_pH*(7-pH)  — difit dari dataset1.csv
    float n_pct = n / 10000.0f;                        // mg/kg -> persen
    float oc    = OC_A0 + OC_AN * n_pct + OC_APH * (7.0f - ph);
    oc = constrain(oc, OC_CMIN, OC_CMAX);              // clamp ke rentang wajar

    float features[6];
    features[IDX_N]  = scaleFeature(n,  IDX_N);
    features[IDX_P]  = scaleFeature(p,  IDX_P);
    features[IDX_K]  = scaleFeature(k,  IDX_K);
    features[IDX_PH] = scaleFeature(ph, IDX_PH);
    features[IDX_EC] = scaleFeature(ec, IDX_EC);
    features[IDX_OC] = scaleFeature(oc, IDX_OC);

    unsigned long start_time = micros();
    int prediction = classifier.predict(features);
    unsigned long latency = micros() - start_time;
    float latency_sec = latency / 1000000.0f;
    Serial.printf("\n[AI Latency: %.6f seconds]\n", latency_sec);

    String aiLabel = "";
    String aiRecom = "";
    showResult(prediction, hum, temp, n, p, k, ph, ec, oc, aiLabel, aiRecom);

    // --- Send to Supabase (Tiap 1 Menit) ---
    if (millis() - lastSupabaseUpdate >= SUPABASE_INTERVAL || lastSupabaseUpdate == 0) {
      lastSupabaseUpdate = millis();
      
      // 1. Simpan data terbaru ke buffer
      addRecord(hum, temp, n, p, k, ph, ec, oc, aiLabel, aiRecom);

      // 2. Cek koneksi Wi-Fi
      if (WiFi.status() != WL_CONNECTED) {
        Serial.printf("[Wi-Fi] Offline! Data ditampung (Buffer: %d/%d)\n", offlineCount, MAX_OFFLINE_RECORDS);
        WiFi.reconnect(); // Coba sambung ulang secara background
      } else {
        Serial.printf("[Supabase] Mengirim %d data tersimpan...\n", offlineCount);
        
        WiFiClientSecure client;
        client.setInsecure(); // Bypass SSL verification
        HTTPClient http;
        
        if (http.begin(client, SUPABASE_URL)) {
          http.addHeader("Content-Type", "application/json");
          http.addHeader("apikey", SUPABASE_KEY);
          String authHeader = String("Bearer ") + SUPABASE_KEY;
          http.addHeader("Authorization", authHeader.c_str());
          http.addHeader("Prefer", "return=minimal");

          // Buat array JSON dinamis (maksimal sekitar 24KB memori heap untuk 60 data + string teks)
          DynamicJsonDocument doc(24000);
          JsonArray array = doc.to<JsonArray>();
          
          for (int i = 0; i < offlineCount; i++) {
            JsonObject obj = array.createNestedObject();
            obj["Hum"] = offlineBuffer[i].hum;
            obj["Temp"] = offlineBuffer[i].temp;
            obj["N"] = offlineBuffer[i].n;
            obj["P"] = offlineBuffer[i].p;
            obj["K"] = offlineBuffer[i].k;
            obj["pH"] = offlineBuffer[i].ph;
            obj["EC"] = (int)offlineBuffer[i].ec;
            obj["OC_est"] = offlineBuffer[i].oc;
            obj["ai_label"] = offlineBuffer[i].label;
            obj["recommendation"] = offlineBuffer[i].recom;
            
            // Sertakan timestamp HANYA JIKA jam sudah pernah tersinkron (NTP berhasil)
            if (offlineBuffer[i].timestamp > 1600000000) {
              struct tm timeinfo;
              localtime_r(&offlineBuffer[i].timestamp, &timeinfo);
              char timeStr[25];
              strftime(timeStr, sizeof(timeStr), "%Y-%m-%dT%H:%M:%S", &timeinfo);
              obj["timestamp"] = timeStr;
            }
          }

          String requestBody;
          serializeJson(doc, requestBody);

          int httpResponseCode = http.POST(requestBody);
          
          if (httpResponseCode == 201) {
            Serial.println("[Supabase] Berhasil mengirim bulk data! Buffer dibersihkan.");
            offlineCount = 0; // Bersihkan buffer setelah data terkirim sukses
          } else {
            Serial.printf("[Supabase] Error code: %d. Data tetap disimpan di buffer.\n", httpResponseCode);
            if (httpResponseCode < 0) {
              Serial.println(http.errorToString(httpResponseCode).c_str());
            }
          }
          http.end();
        } else {
           Serial.println("[Supabase] Gagal inisialisasi HTTP.");
        }
      }
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