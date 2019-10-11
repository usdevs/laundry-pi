import board
import busio
import adafruit_ads1x15.ads1115 as ADS
import datetime as dt
import time

from pin import Pin
from firebase_manager import FirebaseManager
from utils import sg_time_now
from utils import to_py_time
import flagger as fl

from pi_id import PI_ID

def get_pins(pi_id):
    """
    Returns the pins associated with each raspberry pi.
    Update this when new pis/pins are added.
    """
    i2c = busio.I2C(board.SCL, board.SDA)
    ads1 = ADS.ADS1115(i2c, address=0x48)
    ads2 = ADS.ADS1115(i2c, address=0x49)
    ads3 = ADS.ADS1115(i2c, address=0x4a)

    if pi_id == 1:
        return [
            Pin(1, ads1, ADS.P0),
            Pin(2, ads1, ADS.P1),
            Pin(3, ads1, ADS.P2),
            Pin(4, ads1, ADS.P3),
            Pin(5, ads2, ADS.P0),
            Pin(6, ads2, ADS.P1),
            Pin(7, ads2, ADS.P2),
            Pin(8, ads2, ADS.P3),
            Pin(9, ads3, ADS.P0)
        ]

    raise ValueError('Invalid rapsberry pi id : ' + str(pi_id))

def main():

    firebase = FirebaseManager('./usc-laundry-test-firebase-adminsdk-0sph5-01054b85e5.json', PI_ID)
    pins = get_pins(PI_ID)
    flag = fl.Flag(fl.flag)

    # create pins and pis in Firebase if they don't already exist
    firebase.init_pins(pins)
    firebase.init_pi()
    
    all_prev_on = {}
    all_prev_time = {}
    for pin in pins:
        pin_data = firebase.read_pin(pin)
        all_prev_on[pin.id] = pin_data['on']
        all_prev_time[pin.id] = to_py_time(pin_data['timeChanged'])
    
    counter = 0

    # main loop
    while True:
        # updates roughly every 5 min (~30 iterations per min * 5)
        if counter % 150 == 0:
            firebase.update_pi_last_seen(sg_time_now())
            counter = 0
        counter += 1

        # stops the script if a new commit has been detected
        if flag:
            flag.unflag()
            print('Changes were detected. Restarting script...')
            break

        for pin in pins:
            on = pin.is_on()
            now = sg_time_now()

            prev_on = all_prev_on[pin.id]
            prev_time = all_prev_time[pin.id]

            # in seconds. this is only true for washers and tapping once for dryers
            cycle_length = dt.timedelta(minutes=45)

            if (now - prev_time) > cycle_length and on:
                # uh oh, we don't know when the cycle started
                firebase.update_pin_on(pin, on=on, datetime=now, certain=False)
                prev_on = on
                prev_time = time
            elif on != prev_on :
                # update firestore on/off status and timing
                firebase.update_pin_on(pin, on=on, datetime=now, certain=True)
                prev_on = on
                prev_time = now

            all_prev_on[pin.id] = prev_on
            all_prev_time[pin.id] = prev_time

        time.sleep(1)

if __name__ == '__main__':
    main()
