from adafruit_ads1x15.analog_in import AnalogIn # from Adafruit_Python_ADS1x15
import time
import logging
import csv
import datetime as dt

class Pin:
    def __init__(self, id, adc, adc_pin, threshold = 32000, record_values = False):
        """
        Args:
            id (int): Unique ID to every pin (should be unique across RPis too)
            adc (adafruit_ads1x15.ads1115.ADS.ADS1115): Represents one ADC module.
            adc_pin (adafruit_ads1x15.ads1115.ADS.P0/1/2/3): Represents a pin on the ADC module.
            threshold (int, optional): Light threshold. The pin is on if the light value is below
                this threshold.
            record_values (boolean): Whether to record light value readings. Readings
                are recorded in a csv file named pin-<pin ID>.csv.

        Returns:
            A new Pin.
        """
        if type(id) != int:
            raise TypeError('id is {}, which is a {}. It should be an int.'.format(id,type(id)))
        if type(threshold) != int and type(threshold) != float:
            raise TypeError('threshold is {}, which is a {}. It should be a number.'.format(id,type(id)))
        if type(record_values) != bool:
            raise TypeError('record_values is {}, which is a {}. It should be a bool.'.format(id,type(id)))

        self.id = id
        self.adc = adc
        self.adc_pin = adc_pin
        self.threshold = threshold
        self.record_values = record_values

    def is_on_single(self):
        """Checks if this pin is currently on, based on 1 reading. This may return off if the pin is blinking.

        Returns:
            A tuple of whether the pin is on (bool) and the light value reading (int).
        """
        light_value = AnalogIn(self.adc, self.adc_pin).value
#        print(str(self), light_value)
        return light_value < self.threshold, light_value
    
    def is_on(self):
        """Checks whether this pin is on, which includes blinking. Records light values to
        a csv file, if self.record_values is True.

        Returns:
            True if this pin is on or blinking, False otherwise.
            The pin will appear off if it is disconnected.
        """
        log = logging.getLogger()
        values = []
        final_on = False
        for i in range(20):
            on, val = self.is_on_single()
            values.append(val)
            if not final_on and on:
                final_on = True
            time.sleep(0.1)

        log.debug("{} is off. Values:{}".format(self, values))

        if self.record_values:
            with open('pin-' + str(self.id) + '.csv','a+') as f:
                writer = csv.writer(f,quoting=csv.QUOTE_NONNUMERIC)
                now = dt.datetime.now().isoformat()
                rows = map(lambda v: (now,v), values)
                writer.writerows(rows)

        return final_on

    def __str__(self):
        return "Pin {} (threshold={})".format(self.id, self.threshold)

    __repr__ = __str__
