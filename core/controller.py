'''
設備控制器模組，負責協調各種感測器與執行器的操作。
'''
import time
from config import *

from sensors.dht11_sensor import DHT11Sensor
from sensors.turbidity_sensor import TurbiditySensor
from sensors.tds_sensor import TDSSensor
from sensors.water_level_sensor import WaterLevelSensor

from actuators.rgb_led import RGBLed
from actuators.buzzer import Buzzer
from actuators.relay import Relay

from core.wifi_manager import WiFiManager

from typing import Optional
from lib.esplog.core import Logger

from uasyncio import asyncio # type: ignore
import asyncio

class FarmController:
    def __init__(self, pins, logger: Optional[Logger] = None):
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
        # 初始化感測器
        self.dht11 = DHT11Sensor(pin_number=pins['dht11'])
        self.turbidity_sensor = TurbiditySensor(pin_number=pins['turbidity'])
        self.tds_sensor = TDSSensor(pin_number=pins['tds'])
        self.water_level_sensor = WaterLevelSensor(pin_number=pins['water_level'], threshold=WATER_LEVEL_MIN)
        self.logger.debug("感測器初始化完成")
        # 初始化執行器
        self.rgb_led = RGBLed(pins=(pins['rgb_r'], pins['rgb_g'], pins['rgb_b']), common_anode=False)
        self.buzzer = Buzzer(pin_number=pins['buzzer'])
        self.relay_pump = Relay(pin_number=pins['relay_pump'], active_low=True)
        
        self.wifi = WiFiManager(
            ssid=WIFI_SSID, 
            password=WIFI_PASSWORD, 
            logger=self.logger
        )
        self._wifi_task: Optional[asyncio.Task] = None
        
        self.logger.debug("執行器初始化完成")
        self.logger.info("FarmController 初始化完成")
    
    async def init_network(self):
        '''初始化網路連線'''
        ok = await self.wifi.connect(timeout=15)
        if not ok:
            self.logger.warning("啟動時 WiFi 連線失敗，將持續背景重試")
    
    def _dht11_read(self) -> tuple[Optional[float], Optional[float]]:
        '''讀取 DHT11 感測器數據'''
        env = self.dht11.read()
        if env.get("ok"):
            self.logger.debug(f"DHT11 讀取成功: 溫度={env['temp']}°C, 濕度={env['humi']}%")
        else:
            self.logger.error("DHT11 讀取失敗")
        return env["temp"], env["humi"]
    
    def _turbidity_read(self) -> Optional[float]:
        '''讀取濁度感測器數據'''
        turb_percent = self.turbidity_sensor.read_percent()
        if turb_percent is not None:
            self.logger.debug(f"濁度讀取成功: {turb_percent}%")
        else:
            self.logger.error("濁度讀取失敗")
        return turb_percent
    
    def _tds_read(self, temp: float) -> Optional[float]:
        '''讀取 TDS 感測器數據'''
        tds_value = self.tds_sensor.read_tds(temp)
        if tds_value is not None:
            self.logger.debug(f"TDS 讀取成功: {tds_value} ppm")
        else:
            self.logger.error("TDS 讀取失敗")
        return tds_value
    
    def _water_sensor_read(self) -> tuple[Optional[int], Optional[bool]]:
        '''讀取水位感測器數據'''
        water_raw = self.water_level_sensor.read_raw()
        water_low = self.water_level_sensor.is_low()
        if water_raw is not None:
            self.logger.debug(f"水位原始值讀取成功: {water_raw}")
        else:
            self.logger.error("水位原始值讀取失敗")
        
        if water_low is not None:
            self.logger.debug(f"水位狀態判斷成功: 水位過低={water_low}")
        else:
            self.logger.error("水位狀態判斷失敗")
        
        return water_raw, water_low
    
    async def _one_cycle(self):
        '''執行一次監測與控制'''
        # 讀取感測器數據
        # DHT11 讀取溫濕度
        temp, humid = self._dht11_read()
        # turbidity 讀取濁度百分比
        turb_percent = self._turbidity_read()
        # TDS 讀取 TDS 值
        tds_value = self._tds_read(temp) if temp is not None else 25.0
        # 水位感測器讀取原始值與狀態
        water_raw, water_low = self._water_sensor_read()

        # 根據數據進行控制邏輯
        # 異常狀況提示
        alert = False
        if temp is not None and temp > TEMP_HIGH:
            alert = True
            self.logger.warning("溫度過高警告! 建議：開啟冷氣或通風")
            await self.rgb_led.shine_red(duration=0.3, times=3)
            self.rgb_led.warning

        if humid is not None and humid < HUMID_LOW:
            alert = True
            self.logger.warning("濕度過低警告! 建議：使用加濕器或增加環境濕度")
            await self.rgb_led.shine_red(duration=0.3, times=3)
            self.rgb_led.warning

        if turb_percent is not None and turb_percent > TURBIDITY_MAX:
            alert = True
            self.logger.warning("水質濁度過高警告! 建議：檢查水源或更換過濾裝置")
            await self.rgb_led.shine_yellow(duration=0.3, times=3)
            self.rgb_led.warning

        if tds_value is not None and tds_value > TDS_MAX:
            alert = True
            self.logger.warning("水質TDS過高警告! 建議：檢查水源或更換過濾裝置")
            await self.rgb_led.shine_yellow(duration=0.3, times=3)
            self.rgb_led.warning

        if water_low:
            alert = True
            self.logger.warning("水位過低警告! 建議：檢查水源或補充水分")
            await self.rgb_led.shine_blue(duration=0.3, times=3)
            self.rgb_led.warning
            await self.relay_pump.pulse(duration=5.0)  # 啟動水泵5秒
            self.logger.info("水位過低，已啟動水泵進行補水")
            
        if not alert:
            self.rgb_led.ok
            self.buzzer.off()
            self.relay_pump.off()  # 關閉水泵
            self.logger.info("系統狀態正常，所有指標在安全範圍內，等待下一次監測")

        await asyncio.sleep(LOOP_INTERVAL)
        
    async def shutdown(self):
        '''關閉控制器並釋放資源'''
        self.logger.info("關閉 FarmController 中...")
        try:
            self.rgb_led.off()
        except Exception as e:
            self.logger.error(f"關閉 RGB LED 時發生錯誤: {e}")
        
        try:
            self.buzzer.off()
        except Exception as e:
            self.logger.error(f"關閉 Buzzer 時發生錯誤: {e}")
        
        try:
            self.relay_pump.off()
        except Exception as e:
            self.logger.error(f"關閉繼電器水泵時發生錯誤: {e}")
            
        try:
            del self.dht11
            del self.turbidity_sensor
            del self.tds_sensor
            del self.water_level_sensor
            del self.rgb_led
            del self.buzzer
            del self.relay_pump
        except Exception as e:
            self.logger.error(f"釋放資源時發生錯誤: {e}")
        
        if self._wifi_task is not None:
            self._wifi_task.cancel()
            try:
                await self._wifi_task
            except asyncio.CancelledError:
                self.logger.info("WiFi 連接保持任務已取消")
        self.logger.info("FarmController 已關閉")
        
    async def run(self):
        '''持續運行控制器 + 網路初始化'''
        self.logger.info("FarmController 開始運行")
        await self.init_network()
        self._wifi_task = asyncio.create_task(self.wifi.keep_connected())  # 背景持續嘗試連線 WiFi
        try:
            while True:
                await self._one_cycle()
        except KeyboardInterrupt:
            self.logger.info("接收到中斷信號，停止運行FarmController")
        finally:
            await self.shutdown()
    
    def __del__(self):
        '''釋放資源'''
        try:
            del self.dht11
            del self.turbidity_sensor
            del self.tds_sensor
            del self.water_level_sensor
            del self.rgb_led
            del self.buzzer
            del self.relay_pump
            if self._wifi_task is not None:
                self._wifi_task.cancel()
        except Exception as e:
            self.logger.error(f"釋放資源時發生錯誤: {e}")
        self.logger.info("FarmController 資源已釋放")

if __name__ == "__main__":
    async def main():
        fc = FarmController(pins={
            'dht11': DHT11_PIN,
            'turbidity': TURBIDITY_PIN,
            'tds': TDS_PIN,
            'water_level': WATER_LEVEL_PIN,
            'rgb_r': RGB_R_PIN,
            'rgb_g': RGB_G_PIN,
            'rgb_b': RGB_B_PIN,
            'buzzer': BUZZER_PIN,
            'relay_pump': RELAY_PUMP_PIN
        })
        await fc.run()
    asyncio.run(main())