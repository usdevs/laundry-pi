import board # from Adafruit_Blinka
import busio # from Adafruit_Blinka (?)
import adafruit_ads1x15.ads1115 as ADS # from Adafruit_Python_ADS1x15
import datetime as dt
import time
import logger

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

    raise ValueError('invalid rapsberry pi id : ' + str(pi_id))

def main():
    init_logger(config.LOGDIR)
    log = logging.getLogger()

    log.info('main script started.')

    firestore = FirestoreManager(config.FIRESTORE_CERT)
    pins = get_pins(config.PI_ID)
    flag = flagger.Flag(flagger.flag)

    firestore.init_pins(map(pins, lambda p: p.id))
    firestore.init_pi()

    # Initial pin readings
    # For washing machines, ignore lack of changes <= 30 min
    # Can't do this for dryers since they can be paused
    prev_on = {}
    washer_ids = firestore.get_washing_machine_pin_ids()
    for p in pins:
        on = p.is_on()
        prev_on[p.id] = on
        current = firestore.get_pin_data(p.id)
        now = sg_time_now()
        if p.id in washer_ids and on == current['on'] and now - current['time'] <= dt.timedelta(minutes = 30):
            continue
        else:
            firestore.update_pin(p.id, on, sg_time_now(), timeChangedCertain = False)
    
    seconds = 0

    while True:
        # Update pi last seen at least every 10 minutes
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
        seconds += 1

if __name__ == '__main__':
    main()
