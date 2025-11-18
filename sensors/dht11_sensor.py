'''
DHT11 感測器模組
'''
from machine import Pin # type: ignore
import dht # type: ignore
from typing import Dict, Optional

class DHT11Sensor:
    '''
    DHT11 溫濕度感測器類別
    '''
    def __init__(self, pin_number: int):
        """DHT11 感測器的初始化

        Args:
            pin_number (int): DHT11 感測器Data的針腳編號
        """
        self.sensor = dht.DHT11(Pin(pin_number))

    def read(self) -> Dict[str, Optional[float]]:
        """ 讀取溫度並返還

        Returns:
            dict: {'temp': 溫度值, 'humi': 濕度值, 'ok': 是否成功}
        """
        try:
            self.sensor.measure()
            t = self.sensor.temperature()
            h = self.sensor.humidity()
            return {'temp': t, 'humi': h, 'ok': True}
        except Exception as e:
            print("DHT11 讀取失敗:", e)
            return {'temp': None, 'humi': None, 'ok': False}
    
    def __del__(self):
        '''釋放資源'''
        del self.sensor
        print("DHT11 感測器資源已釋放")
        
if __name__ == "__main__":
    dht11 = DHT11Sensor(pin_number=15)  # 假設DHT11連接在GPIO14
    data = dht11.read()
    print("溫度:", data['temp'], "°C")
    print("濕度:", data['humi'], "%")