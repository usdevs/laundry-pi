from adafruit_ads1x15.analog_in import AnalogIn

class Pin:
    def __init__(self, id, adc, adc_pin, threshold = 32000):
        """id: integer id unique to every pin/pi. adc: adafruit_ads1x15.ads1115.ADS object"""
        self.id = id
        self.adc = adc
        self.adc_pin = adc_pin
        self.threshold = threshold

    def is_on_single(self):
        light_value = AnalogIn(self.adc, self.adc_pin).value
        print(self.id, light_value)
        return light_value < self.threshold
    
    def is_on(self):
        """Allow blinking"""
        for i in range(20):
            if self.is_on_single():
                return True
        return False

    def __str__(self):
        return 'Pin ' + self.id

    __repr__ = __str__
