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
        while True:
            if not self.is_connected():
                self.logger.warning("WiFi 連接中斷，嘗試重新連接...")
                ok = await self.connect(timeout=timeout)
                if not ok:
                    self.logger.error("重新連接 WiFi 失敗")
            await asyncio.sleep(check_interval)