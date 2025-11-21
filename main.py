from core.wifi_manager import WiFiManager
from core.controller import FarmController
from lib.esplog.core import Logger
from config import *
import asyncio

def main():
    logger = Logger(
        level="DEBUG",
        log_to_console=True,
        log_to_file=True,
        file_name="farm_controller.txt",
        max_file_size=1024,
        use_colors=True,
        log_format="text"
    )
    
    pins = {
        'dht11': DHT11_PIN,
        'turbidity': TURBIDITY_PIN,
        'tds': TDS_PIN,
        'water_level': WATER_LEVEL_PIN,
        'rgb_r': RGB_R_PIN,
        'rgb_g': RGB_G_PIN,
        'rgb_b': RGB_B_PIN,
        'buzzer': BUZZER_PIN,
        'relay_pump': RELAY_PUMP_PIN
    }
    
    controller = FarmController(pins=pins, logger=logger)

    async def run_controller():
        await controller.run()
        # 在此處添加更多控制邏輯，例如定期讀取感測器數據並控制執行器
    
    asyncio.run(run_controller())


if __name__ == "__main__":
    main()
