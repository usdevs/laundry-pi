from firebase_manager import FirebaseManager
from utils import sg_time_now

# dummy pin for testing
class Pin:
    def __init__(self, id, adc, adc_pin, threshold = 32000, dummy_on_values = (True, False)):
        """id: integer id unique to every pin/pi. adc: adafruit_ads1x15.ads1115.ADS object"""
        self.id = id
        self.adc = adc
        self.adc_pin = adc_pin
        self.threshold = threshold
        self.dummy_on_values = dummy_on_values
        self.counter = -1

    def is_working(self):
        return True # TODO this properly

    def is_on(self):
        if self.counter == len(self.dummy_on_values) - 1:
            self.counter = 0
        else:
            self.counter += 1
        return self.dummy_on_values[self.counter]

def main():
    TEST_CERT = '' # Fill this in before testing 
    firebase = FirebaseManager(TEST_CERT, 2)
  
    pin1 = Pin(1,None,None,dummy_on_values = (False, True))
    pin2 = Pin(2, None, None)
    pin3 = Pin(3, None, None)
    
    firebase.init_pins([pin1, pin2, pin3])
    firebase.init_pi()

    # test existing pin
    firebase.update_pin_on(pin1, True, sg_time_now(), True)

    # test new pin
    print(firebase.read_pin(pin2))
    firebase.update_pin_on(pin2, True, sg_time_now(), True)
    

    # test rpi
    firebase.update_pi_last_seen(sg_time_now())

    # check return types
    print(type(firebase.get_pi_last_seen()))
    pin1_data = firebase.read_pin(pin1)
    for k, v in pin1_data.items():
        print(k, v)
        print(type(k))
        print(type(v))

if __name__ == '__main__':
    main()
