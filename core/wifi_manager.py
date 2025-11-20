'''
WiFi 管理模組，負責連接與管理 WiFi 連線。
'''
from uasyncio import asyncio # type: ignore
import network  # type: ignore
import time
from typing import Optional
from lib.esplog.core import Logger

class WiFiManager:
    def __init__(self, ssid: str, password: str, logger: Optional[Logger] = None):
        """WiFiManager 的初始化

        Args:
            ssid (str): WiFi SSID
            password (str): WiFi 密碼
            logger (Optional[Logger]): 日誌記錄器，預設為 None
        """
        self.ssid = ssid
        self.password = password
        if logger:
            self.logger = logger
        else:
            self.logger = Logger(
                    level="DEBUG",
                    log_to_console=True,
                    log_to_file=True,
                    file_name="farm_controller.txt",
                    max_file_size=1024,
                    use_colors=True,
                    log_format="text"
            )
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
    
    def is_connected(self) -> bool:
        """檢查是否已連接到 WiFi

        Returns:
            bool: 已連接返回 True，否則返回 False
        """
        return self.wlan.isconnected()
    
    async def connect(self, timeout: int = 15) -> bool:
        """連接到 WiFi 網路

        Args:
            timeout (int): 連接超時時間（秒），預設為 15 秒

        Returns:
            bool: 連接成功返回 True，否則返回 False
        """
        if self.is_connected():
            self.logger.info("已經連接到 WiFi")
            return True
        
        self.logger.info(f"嘗試連接到 WiFi SSID: {self.ssid}")
        self.wlan.connect(self.ssid, self.password)
        
        start_time = time.time()
        while not self.is_connected():
            if time.time() - start_time > timeout:
                self.logger.error("WiFi 連接超時")
                return False
            await asyncio.sleep(1)
        
        self.logger.info(f"WiFi 連接成功，IP 地址: {self.wlan.ifconfig()[0]}")
        return True

    async def keep_connected(self, check_interval: int = 10, timeout: int = 10):
        """持續檢查並保持 WiFi 連接

        Args:
            check_interval (int): 檢查間隔時間（秒），預設為 10 秒
        """
        try:
            while True:
                if not self.is_connected():
                    self.logger.warning("WiFi 連接中斷，嘗試重新連接...")
                    ok = await self.connect(timeout=timeout)
                    if not ok:
                        self.logger.error("重新連接 WiFi 失敗")
                await asyncio.sleep(check_interval)
        except asyncio.CancelledError:
            self.logger.info("WiFi 連接保持任務已取消")
        finally:
            self.logger.info("WiFi 連接保持任務結束")
            self.wlan.disconnect()


if __name__ == "__main__":
    """
    簡單測試 WiFiManager 的用法：
    - 啟動時嘗試連線一次
    - 成功後啟動 keep_connected 背景任務
    - 主程式每 3 秒印一次心跳與連線狀態
    - Ctrl+C 中斷時優雅結束
    """

    # ⚠️ 記得把這兩個換成你實際的 WiFi 資訊
    TEST_WIFI_SSID = "Your_WiFi_SSID"
    TEST_WIFI_PASSWORD = "Your_WiFi_Password"

    async def main():
        # 建立 Logger
        logger = Logger(
            level="DEBUG",
            log_to_console=True,
            log_to_file=True,
            file_name="wifi_test.log",
            max_file_size=1024,
            use_colors=True,
            log_format="text"
        )

        logger.info("=== WiFiManager 測試程式啟動 ===")

        wifi = WiFiManager(
            ssid=TEST_WIFI_SSID,
            password=TEST_WIFI_PASSWORD,
            logger=logger
        )

        # 1️⃣ 先嘗試連線一次
        logger.info("開始嘗試連線 WiFi ...")
        ok = await wifi.connect(timeout=15)
        if not ok:
            logger.error("首次連線失敗，結束測試")
            return

        ip = wifi.wlan.ifconfig()[0]
        logger.info(f"首次連線成功，IP: {ip}")

        # 2️⃣ 開啟背景 keep_connected 任務
        logger.info("啟動 keep_connected 背景任務")
        keep_task = asyncio.create_task(
            wifi.keep_connected(check_interval=5, timeout=10)
        )

        # 3️⃣ 模擬主程式邏輯：每 3 秒印一次心跳
        try:
            i = 0
            while True:
                i += 1
                logger.info(f"[主程式] 心跳 {i}，WiFi 狀態: {wifi.is_connected()}")
                await asyncio.sleep(3)
        except KeyboardInterrupt:
            logger.info("收到中斷信號，準備結束測試")
        finally:
            logger.info("取消 keep_connected 背景任務")
            keep_task.cancel()
            # 讓 CancelledError 有機會被處理
            await asyncio.sleep(0)
            logger.info("WiFiManager 測試程式結束")

    try:
        asyncio.run(main())
    except AttributeError:
        # 舊版 uasyncio 沒有 run() 的相容處理
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())