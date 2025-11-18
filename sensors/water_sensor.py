'''
水碰到就導通
-> 水位感測器
因有生鏽問題，不用來長期監測水位
所以用作為短期的水漏偵測
'''
from machine import Pin, ADC # type: ignore
from typing import Optional

class WaterLevelSensor:
    '''
    水感測器類別
    '''
    def __init__(self, pin_number: int, threshold: int = 1000):
        """水感測器的初始化

        Args:
            pin_number (int): 水感測器的針腳編號
            threshold (int): 水感測器的閾值
        """
        adc = ADC(Pin(pin_number))
        adc.atten(ADC.ATTN_11DB)  # 設定量程為0-3.3V
        adc.width(ADC.WIDTH_12BIT)  # 設定解析度為12位元
        self._adc = adc
        self._threshold = threshold

    def read_raw(self) -> int:
        """ 讀取原始ADC值並返還

        Returns:
            int: 原始ADC值 (0-4095)
        """
        try:
            raw_value = self._adc.read() # 0-4095
            return raw_value
        except Exception as e:
            print("水感測器原始值讀取失敗:", e)
            return -1
    
    def is_low(self) -> Optional[bool]:
        """ 判斷是否有水接觸

        Returns:
            bool: 有水接觸返回True，否則返回False
        """
        try:
            return self.read_raw() > self._threshold
        except Exception as e:
            print("水感測器濕度判斷失敗:", e)
            return None
    
    def __del__(self):
        '''釋放資源'''
        del self._adc
        print("水感測器資源已釋放")

if __name__ == "__main__":
    water_sensor = WaterLevelSensor(pin_number=32)  # 假設水感測器連接到GPIO32
    raw_value = water_sensor.read_raw()
    wet_status = water_sensor.is_low()
    print(f"水感測器原始值: {raw_value}")
    print(f"是否有水接觸: {'是' if wet_status else '否'}")