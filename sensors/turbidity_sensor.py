'''
TDS 感測器模組
'''
from machine import ADC, Pin # type: ignore
from typing import Optional

class TurbiditySensor:
    '''
    TDS 濁度感測器類別
    '''
    def __init__(self, pin_number: int):
        """TDS 感測器的初始化

        Args:
            pin_number (int): TDS 感測器的針腳編號
        """
        adc = ADC(Pin(pin_number))
        adc.atten(ADC.ATTN_11DB)  # 設定量程為0-3.3V
        adc.width(ADC.WIDTH_12BIT)  # 設定解析度為12位元
        self._adc = adc

    def read_raw(self) -> int:
        """ 讀取原始ADC值並返還

        Returns:
            int: 原始ADC值 (0-4095)
        """ 
        try:
            raw_value = self._adc.read() # 0-4095
            return raw_value
        except Exception as e:
            print("TDS 原始值讀取失敗:", e)
            return -1
        
    def read_percent(self) -> Optional[float]:
        """ 讀取濁度百分比並返還

        Returns:
            float: 濁度百分比 (0.0-100.0)
        """
        try:
            raw_value = self.read_raw()
            clarity = (raw_value / 4095) * 100.0
            turbidity = 100.0 - clarity
            return turbidity
        except Exception as e:
            print("TDS 百分比讀取失敗:", e)
            return None
    
    def __del__(self):
        '''釋放資源'''
        del self._adc
        print("TDS 感測器資源已釋放")

if __name__ == "__main__":
    turbidity_sensor = TurbiditySensor(pin_number=34)  # 假設TDS感測器連接到GPIO34
    raw_value = turbidity_sensor.read_raw()
    turbidity_value = turbidity_sensor.read_percent()
    print(f"TDS 原始值: {raw_value}")
    print(f"TDS 濁度百分比: {turbidity_value} %")   