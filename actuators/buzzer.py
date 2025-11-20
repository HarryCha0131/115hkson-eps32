'''
Buzzer 蜂鳴器模組
'''
from machine import Pin, PWM # type: ignore
from typing import Optional
import asyncio

class Buzzer:
    def __init__(self, pin_number: int, freq: int = 1000):
        """Buzzer 蜂鳴器的初始化

        Args:
            pin_number (int): 蜂鳴器的針腳編號
            freq (int): 蜂鳴器的頻率，預設為1000 Hz
        """
        self.pwm = PWM(Pin(pin_number))
        self.pwm.freq(freq)
        self.pwm.duty(0)
        self.freq = freq
        self.off()
    
    def off(self):
        """關閉蜂鳴器"""
        self.pwm.duty(0)
    
    async def alarm_pattern(self, pattern: list):
        """根據給定的模式發出蜂鳴聲

        Args:
            pattern (list): 包含持續時間的列表，正值表示蜂鳴，負值表示靜音
        """
        try:
            for duration in pattern:
                if duration > 0:
                    self.pwm.duty(512)  # 開啟蜂鳴器
                else:
                    self.pwm.duty(0)    # 關閉蜂鳴器
                await asyncio.sleep(abs(duration))
            self.off()
        except Exception as e:
            print("蜂鳴器模式發聲失敗:", e)
    
    async def beep(self, duration: float = 0.5):
        """發出單次蜂鳴聲

        Args:
            duration (float): 蜂鳴持續時間，預設為0.5秒
        """
        try:
            await self.alarm_pattern([duration])
        except Exception as e:
            print("蜂鳴器單次發聲失敗:", e)
    
    async def dididi(self):
        """發出滴滴聲模式"""
        pattern = [0.1, 0.1, -0.2, 0.1, 0.1, -0.2, 0.1, 0.1]
        await self.alarm_pattern(pattern)

    def __del__(self):
        '''釋放資源'''
        self.off()
        del self.pwm
        print("蜂鳴器資源已釋放")

if __name__ == "__main__":
    async def main():
        buzzer = Buzzer(pin_number=23)  # 假設蜂鳴器連接到GPIO23
        print("發出單次蜂鳴聲")
        await buzzer.beep(duration=0.5)
        await asyncio.sleep(1)
        print("發出滴滴聲模式")
        await buzzer.dididi()
    asyncio.run(main())