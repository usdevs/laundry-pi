from adafruit_ads1x15.analog_in import AnalogIn # from Adafruit_Python_ADS1x15
import time
import logging

class Pin:
    def __init__(self, id, adc, adc_pin, threshold = 32000):
        """
        Args:
            id (int): Unique ID to every pin (should be unique across RPis too)
            adc (adafruit_ads1x15.ads1115.ADS.ADS1115): Represents one ADC module.
            adc_pin (adafruit_ads1x15.ads1115.ADS.P0/1/2/3): Represents a pin on the ADC module.
            threshold (int, optional): Light threshold. The pin is on if the light value is below
                this threshold.

        Returns:
            A new Pin.
        """
        self.id = id
        self.adc = adc
        self.adc_pin = adc_pin
        self.threshold = threshold

    def is_on_single(self):
        """Checks if this pin is currently on, based on 1 reading. This may return off if the pin is blinking.

        Returns:
            A tuple of whether the pin is on (bool) and the light value reading (int).
        """
        light_value = AnalogIn(self.adc, self.adc_pin).value
#        print(str(self), light_value)
        return light_value < self.threshold, light_value
    
    def is_on(self):
        """Checks whether this pin is on, which includes blinking.

        Returns:
            True if this pin is on or blinking, False otherwise.
            The pin will appear off if it is disconnected.
        """
        log = logging.getLogger()
        values = []
        for i in range(20):
            on, val = self.is_on_single()
            values.append(val)
            if on:
                log.debug("{} is on. Values:{}".format(self, values))
                return True
            time.sleep(0.1)

        log.debug("{} is off. Values:{}".format(self, values))
        return False

    def __str__(self):
        return "Pin {} (threshold={})".format(self.id, self.threshold)

    __repr__ = __str__
