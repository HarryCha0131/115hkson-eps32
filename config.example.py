# config.example.py
# 請將本檔案複製為 config.py 並填入實際的設備設定與憑證

# ------------ pins ------------
DHT11_PIN = 13          # 例：GPIO13
TURBIDITY_PIN = 34      # ADC1 channel
TDS_PIN = 35            # ADC1 channel
WATER_LEVEL_PIN = 32    # ADC1 channel

RGB_R_PIN = 33
RGB_G_PIN = 25
RGB_B_PIN = 26

BUZZER_PIN = 23
RELAY_PUMP_PIN = 18

# ------------ thresholds（依實測調整）------------
TEMP_LOW = 15.0
TEMP_HIGH = 35.0
HUMID_LOW = 40.0
HUMID_HIGH = 70.0

TURBIDITY_MAX = 2500
TDS_MAX = 700
WATER_LEVEL_MIN = 1000

# 系統更新頻率（秒）
LOOP_INTERVAL = 5
DATA_UPLOAD_INTERVALS = 12  # 例：每 12 次迴圈上傳一次（若 LOOP_INTERVAL=5 秒，約每分鐘一次）

# WiFi 設定（請填真實值後再同步到設備，勿提交）
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"

# Webhook URLs（請改成你的測試/正式環境）
MAKE_WEBHOOK_URL = "https://example.com/make-webhook"
WEBHOOK_URL = "http://localhost:1567/data/webhook"
