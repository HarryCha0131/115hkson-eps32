'''
LED RGB 觸發器模組
'''
from machine import Pin, PWM # type: ignore
from typing import Tuple
from uasyncio import asyncio # type: ignore
import asyncio

class RGBLed:
    def __init__(self, pins: Tuple[int, int, int], freq: int = 1000, common_anode: bool = False):
        """RGB LED 的初始化

        Args:
            pins (Tuple[int, int, int]): RGB LED 的三個針腳編號 (R, G, B)
            freq (int): PWM 頻率，預設為1000Hz
            common_anode (bool): 是否為共陽極，預設為False (共陰極)
        """
        self.inverted = common_anode
        self.r, self.g, self.b = map(lambda pin: PWM(Pin(pin), freq=freq), pins)
        self.max_duty = 1023  # ESP32 的 PWM 最大值為 1023
        
    def _set_channel(self, channel: PWM, value: int):
        """設定單一顏色通道的亮度

        Args:
            channel (PWM): PWM 通道
            value (int): 0-255 的亮度值
        """
        duty = int((value / 255) * self.max_duty)
        if self.inverted:
            value = self.max_duty - value
        channel.duty(duty)
    
    def set_rgb(self, r: int, g: int, b: int):
        """設定 RGB LED 的顏色

        Args:
            r (int): 紅色亮度 (0-255)
            g (int): 綠色亮度 (0-255)
            b (int): 藍色亮度 (0-255)
        """
        self._set_channel(self.r, r)
        self._set_channel(self.g, g)
        self._set_channel(self.b, b)
    
    def green(self): self.set_rgb(0, 255, 0)
    def red(self): self.set_rgb(255, 0, 0)
    def blue(self): self.set_rgb(0, 0, 255)
    def yellow(self): self.set_rgb(255, 255, 0)
    def off(self): self.set_rgb(0, 0, 0)

    async def _shine(self, r: int, g: int, b: int, duration: float= 0.5, times: int=2):
        '''閃爍提示'''
        for _ in range(times):
            self.set_rgb(r, g, b)
            await asyncio.sleep(duration)
            self.off()
            await asyncio.sleep(duration)
            
    async def shine_green(self, duration: float= 0.5, times: int=2):
        await self._shine(0, 255, 0, duration, times)
    async def shine_red(self, duration: float= 0.5, times: int=2):
        await self._shine(255, 0, 0, duration, times)
    async def shine_blue(self, duration: float= 0.5, times: int=2):
        await self._shine(0, 0, 255, duration, times)
    async def shine_yellow(self, duration: float= 0.5, times: int=2):
        await self._shine(255, 255, 0, duration, times)

    ok = property(green)
    working = property(blue)
    warning = property(yellow)
    error = property(red)
    
    def __del__(self):
        '''釋放資源'''
        self.red.deinit() # type: ignore
        self.green.deinit() # type: ignore
        self.blue.deinit() # type: ignore
        print("RGB LED 資源已釋放")

if __name__ == "__main__":
    async def main():
        rgb_led = RGBLed(pins=(25, 26, 27), common_anode=False)  # 假設RGB LED連接到GPIO25(R), GPIO26(G), GPIO27(B)
        print("設定為紅色")
        rgb_led.red()
        await asyncio.sleep(2)
        print("設定為綠色")
        rgb_led.green()
        await asyncio.sleep(2)
        print("設定為藍色")
        rgb_led.blue()
        await asyncio.sleep(2)
        print("關閉LED")
        rgb_led.off()
        # 測試properties
        print("設定為工作狀態(藍色)")
        rgb_led.working
        await asyncio.sleep(2)
        print("設定為錯誤狀態(紅色)")
        rgb_led.error
        await asyncio.sleep(2)
        print("設定為正常狀態(綠色)")
        rgb_led.ok
        await asyncio.sleep(2)
        print("關閉LED")
        rgb_led.off()

    asyncio.run(main())