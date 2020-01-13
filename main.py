import board # from Adafruit-Blinka
import busio # from Adafruit-Blinka
import adafruit_ads1x15.ads1115 as ADS # from Adafruit_Python_ADS1x15
import datetime as dt
import time
import logging

from pin import Pin
from firestore_manager import FirestoreManager
from utils import sg_time_now, to_py_time, init_logger
import flagger
import config

def get_pins(pi_id):
    """Returns the pins associated with each RPi. Update this when new RPis/pins are added."""
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

    elif pi_id == 2:
        return [
            Pin(10, ads1, ADS.P0),
            Pin(11, ads1, ADS.P1),
            Pin(12, ads1, ADS.P2),
            Pin(13, ads1, ADS.P3, threshold = 16000),
            Pin(14, ads2, ADS.P0),
            Pin(15, ads2, ADS.P1),
            Pin(16, ads2, ADS.P2),
            Pin(17, ads2, ADS.P3),
            Pin(18, ads3, ADS.P0),
        ]

    raise ValueError('invalid rapsberry pi id : ' + str(pi_id))

def main():
    init_logger(config.LOGDIR)
    log = logging.getLogger()

    log.info('main script started.')

    firestore = FirestoreManager(config.FIRESTORE_CERT, config.PI_ID)
    pins = get_pins(config.PI_ID)
    flag = flagger.Flag(flagger.flag)

    firestore.init_pins(map(lambda p: p.id, pins))
    firestore.init_pi()

    # Initial pin readings
    # For washing machines, ignore lack of change within 30 min
    # For dryers, ignore lack of change within 45 min
    prev_on = {}
    washer_ids = firestore.get_washing_machine_pin_ids()
    for p in pins:
        on = p.is_on()
        prev_on[p.id] = on
        current = firestore.get_pin_data(p.id)
        now = sg_time_now()
        timediff = now - current['timeChanged']
        if on == current['on'] and p.id in washer_ids and timediff <= dt.timedelta(minutes=30) or \
           timediff <= dt.timedelta(minutes=45): 
            continue
        else:
            firestore.update_pin(p.id, on, sg_time_now(), timeChangedCertain = False)

    seconds = 0

    while True:
        # Update pi last seen at least every 5 minutes
        if seconds == 600:
            firestore.update_pi_last_seen()
            seconds = 0

        # Check if any pins have changed
        for p in pins:
            on = p.is_on()
            if on != prev_on[p.id]:
                firestore.update_pin(p.id, on, sg_time_now())
                prev_on[p.id] = on
                seconds = 0

        # Check for updates from Github
        if flag.flagged():
            flag.unflag()
            log.info('changes from github were detected. restarting main script.')
            break

        time.sleep(1)
        seconds += 25 # takes about 25 seconds to update 9 pins
        log.debug("{} seconds".format(seconds))

if __name__ == '__main__':
    main()
