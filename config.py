# config.py

# ------------ pins ------------
DHT11_PIN = 5     # 例：GPIO4
TURBIDITY_PIN = 34    # ADC1 channel
TDS_PIN = 35          # ADC1 channel
WATER_LEVEL_PIN = 32  # ADC1 channel

RGB_R_PIN = 25
RGB_G_PIN = 26
RGB_B_PIN = 27

BUZZER_PIN = 14
RELAY_PUMP_PIN = 17

# ------------ thresholds（可以之後再調）------------
TEMP_LOW = 15.0           # 太冷
TEMP_HIGH = 35.0          # 太熱
HUMID_LOW = 40.0          # 太乾
HUMID_HIGH = 70.0         # 太濕

TURBIDITY_MAX = 2500      # ADC 原始值範例（越高越混）
TDS_MAX = 700             # ppm（要配合實測調整）

WATER_LEVEL_MIN = 1000    # ADC：低於代表沒水 / 水位太低

# 系統更新頻率（秒）
LOOP_INTERVAL = 5