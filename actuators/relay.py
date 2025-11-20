'''
relay 繼電器控制模組
用作控制水泵
'''
from machine import Pin # type: ignore
import asyncio

class Relay:
    def __init__(self, pin_number: int, active_low: bool = True):
        """繼電器的初始化

        Args:
            pin_number (int): 繼電器的針腳編號
            active_high (bool): 繼電器是否為高電平觸發，預設為True
        """
        self.pin = Pin(pin_number, Pin.OUT)
        self.active_low = active_low
        self.off()
    
    def on(self):
        """啟動繼電器"""
        self.pin.value(0 if self.active_low else 1)
            
    def off(self):
        """關閉繼電器"""
        self.pin.value(1 if self.active_low else 0)
        
    async def pulse(self, duration: float = 1.0):
        """啟動繼電器一段時間後自動關閉
        """
        self.on()
        await asyncio.sleep(duration)
        self.off()
    
    def is_on(self) -> bool:
        """檢查繼電器是否啟動

        Returns:
            bool: 繼電器啟動返回True，否則返回False
        """
        return self.pin.value() == (0 if self.active_low else 1)
    
    
    def __del__(self):
        '''釋放資源'''
        del self.pin
        print("繼電器資源已釋放")
    
if __name__ == "__main__":
    async def main():
        relay = Relay(pin_number=18, active_low=True)  # 假設繼電器連接到GPIO18
        print("啟動繼電器3秒...")
        relay.on()
        await asyncio.sleep(3)
        print("關閉繼電器")
        relay.off()
        print("繼電器脈衝啟動2秒...")
        await relay.pulse(duration=2.0)

    asyncio.run(main())