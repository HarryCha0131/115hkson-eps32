# 智慧農場控制系統（ESP32 / MicroPython）

這是一個把「感測器 + 執行器 + Wi‑Fi 上傳」串在一起的簡單農場控制專案。設計給大一新生也看得懂：用 ESP32 蒐集溫溼度、濁度、TDS、水位，再用燈、蜂鳴器、繼電器做提醒或補水，並把平均值上傳到 Webhook。專業人士也能快速找到模組分工與流程。

## 先裝好再開跑

-   主機端 Python 3.12；板子跑 MicroPython。
-   安裝依賴（主機側工具與模擬腳本）：`uv sync --dev`（或 `pip install -e .[dev]`）。
-   把檔案複製到 ESP32（用 Thonny 或 `mpremote cp ...`），確保 `config.py` 填好 Wi‑Fi 與 Webhook。
-   在板子上跑主程式：Thonny 直接執行或`mpremote run main.py`。
-   想測試 API 而不接硬體：`python fake_upload.py` 會把假資料送到 `config.py` 的 `WEBHOOK_URL`（亦或者自行更改需要的 URL 即可）。

## 專案地圖（每個資料夾做什麼）

-   `main.py`：入口，建立 logger、引腳表，啟動 `FarmController.run()`。
-   `config.py`：腳位、閾值、Wi‑Fi、Webhook。請替換成你自己的設定，避免把真實密碼推上 Git。
-   `core/controller.py`：大腦。讀感測器 → 判斷閾值 → 控制 LED/蜂鳴器/水泵 → 累積歷史 → 定期上傳。
-   `core/wifi_manager.py`：連線 Wi‑Fi、背景重連、NTP 校時。
-   `sensors/`：硬體讀值
    -   `dht11_sensor.py`：溫溼度。
    -   `turbidity_sensor.py`：濁度百分比。
    -   `tds_sensor.py`：ADC 轉 TDS ppm。
    -   `water_sensor.py`：水位 ADC 與低水位判斷。
-   `actuators/`：硬體動作
    -   `rgb_led.py`：用顏色/閃爍表示狀態。
    -   `buzzer.py`：蜂鳴器開關。
    -   `relay.py`：控制水泵繼電器（active low）。
-   `lib/`：設備端工具集合，包含輕量 logger（此模組來自他人 GitHub，請補上原作者與連結）、精簡版 HTTP 需求，以及可能會用到的 Wi‑Fi 輔助工具。
-   `fake_upload.py`：造假資料丟 Webhook，方便前後端對接測試。

## 控制迴圈怎麼跑

1. 啟動感測器/執行器，建立 Wi‑Fi 背景重連任務。
2. 每回合讀溫溼度、濁度、TDS、水位並比對閾值。
3. 有異常就亮指定顏色、鳴叫或啟動水泵；正常就待機。
4. 把每回合資料存進 `FarmHistoryData`，累積到 `DATA_UPLOAD_INTERVALS` 就平均後上傳到 Webhook。
5. 收到中斷時關閉硬體與 Wi‑Fi 任務，釋放資源。

## 安全與設定提醒

-   `config.py` 的 Wi‑Fi 密碼與 Webhook URL 請改成你自己的，別推到公開倉庫。
-   閾值要依實測微調；`LOOP_INTERVAL` 與 `DATA_UPLOAD_INTERVALS` 可調整上傳頻率。

## 開發與除錯小撇步

-   優先用 `lib.esplog.core.Logger` 記錄訊息，檔案預設 `farm_controller.txt`，比 `print` 更好追蹤。
-   感測器讀不到或 Wi‑Fi 斷線會在 log 警示，修好線路或設定後再跑即可。
-   要加新感測器/執行器，可以參考 `sensors/*`、`actuators/*` 的封裝與例外處理，保持 async 友善、避免阻塞。

## Acknowledgements

This project partially builds upon the work of **ESPlog** by Arman Ghobadi, released under the MIT License.  
Original repository: https://github.com/armanghobadi/esplog

Thanks to Arman for the excellent open-source logger designed for MicroPython / ESP microcontrollers.
