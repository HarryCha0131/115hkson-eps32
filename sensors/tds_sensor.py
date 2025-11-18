'''
TDS 感測器模組
'''
from typing import Optional
from machine import ADC, Pin # type: ignore

class TDSSensor:
    '''
    TDS 濁度感測器類別
    '''
    def __init__(self, pin_number: int, vref: float = 3.3):
        """TDS 感測器的初始化

        Args:
            pin_number (int): TDS 感測器的針腳編號
        """
        adc = ADC(Pin(pin_number))
        adc.atten(ADC.ATTN_11DB)  # 設定量程為0-3.3V
        adc.width(ADC.WIDTH_12BIT)  # 設定解析度為12位元
        self._adc = adc
        self._vref = vref

    def read_voltage(self) -> float:
        """ 讀取原始ADC值並返還對應的電壓值

        Returns:
            float: 原始ADC值 (0-4095) 對應的電壓值 (V)
        """
        try:
            raw_value = self._adc.read() # 0-4095
            return raw_value * (self._vref / 4095.0)
        except Exception as e:
            print("TDS 原始值讀取失敗:", e)
            return -1
        
    def read_tds(self, temp_c: float = 25.0) -> Optional[float]:
        """ 讀取估算的TDS值並返還

        Returns:
            float: 估算的TDS值 (ppm)
        """
        try:
            v = self.read_voltage()
            compensation = 1.0 + 0.02 * (temp_c - 25.0)  # 假設溫度為25度C
            v_compensated = v / compensation
            tds = (133.42 * v_compensated**3 - 255.86 * v_compensated**2 + 857.39 * v_compensated) * 0.5
            return tds
        except Exception as e:
            print("TDS 估算值讀取失敗:", e)
            return None
    
    def __del__(self):
        '''釋放資源'''
        del self._adc
        print("TDS 感測器資源已釋放")

if __name__ == "__main__":
    tds_sensor = TDSSensor(pin_number=35)  # 假設TDS感測器連接到GPIO34
    raw_value = tds_sensor.read_voltage()
    tds_value = tds_sensor.read_tds()
    print(f"TDS 原始值: {raw_value}")
    print(f"TDS 估算值: {tds_value} ppm")

