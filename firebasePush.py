import asyncio
import time
import board
import busio
import firebase_admin
import time
from firebase_admin import credentials
from firebase_admin import firestore
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

FIREBASE_CERT = './usc-laundry-test-firebase-adminsdk-0sph5-01054b85e5.json'
FIREBASE_COLLECTION = 'test_collection'
FIREBASE_DOCUMENT = 'test_document'
THRESHHOLD = 32000

class FirebaseManager:
    def __init__(self, cert, interval=0.5):
        self.db = self.init_database(cert)
        self.machines = list()

    def init_database(self, cert):
        cred = credentials.Certificate(cert)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        doc = db.collection(FIREBASE_COLLECTION).document(FIREBASE_DOCUMENT)
        return doc

    def run(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.main())

    async def push_status_update(self, machine):
        """Pushes a firebase update from a machine if it exists"""
        status = await machine.status()
        if status:
            self.db.set(status, merge=True)
        
    async def main(self):
        while True:
            tasks = [self.push_status_update(machine) for machine in self.machines]
            done, pending = await asyncio.wait(tasks, timeout=self.interval)
            for task in pending:
                print('failed to push!')
                task.cancel()

class LaundryMachine:
    def __init__(self, name, sensor):
        self.name = name
        self.running = None

    async def status(self, record):
        """Returns a firebase update if the machine changes states"""
        results = dict()
        running = await self.sensor.status()
        if running != self.running:
            results.update({
                f'{self.name}_running': self.running,
                f'{self.name}_time': time.time(),
            })
            self.running = running
        return results

class SensorADS1115(ADS.ADS1115):
    async def status(self):
        """Returns if door lock light is on"""
        lightness = AnalogIn(self, ADS.P0).value
        return lightness < THRESHHOLD

async def main():
    # Initialize firebase
    fb = FirebaseManager(CERT_PATH, interval=0.5)

    """
    HACK START
    - Ratchet way to debug IP from the Pi
    - Alternatively, schedule ip-patch.py on CRON
    - source at /home/pi/laundroAY1920/ip-patch.py
    ---
    import socket

    try:
        print('trying IP hack!')
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8",80))
            ip_address = s.getsockname()[0]
            if ip_address != '127.0.0.1':
                HACK_update = {
                    'HACK timestamp': time.strftime('%x %X'),
                    'HACK ipaddress': ip_address,
                }
                fb.doc.set(HACK_update, merge=True)
    except:
        print('IP hack failed ):')
    ---
    HACK END
    """

    # Create the I2C bus
    i2c = busio.I2C(board.SCL, board.SDA)

    # Create ADC object using I2C bus
    ads_input = {
        'name1': SensorADS1115(i2c, address=0x49)),
        'name2': SensorADS1115(i2c, address=0x48)),
        'name3': SensorADS1115(i2c, address=0x4a)),
    }

    # Passes ADCs to firebase Object (I resist the one liner)
    # fb.machines.extend(LaundryMachine(*input) for input in ads_input.items())
    for name, sensor in ads_input.items():
        machine = LaundryMachine(name, sensor)
        fb.machines.append(machine)

    # Hope for the best!
    await fb.run())

if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())

    except Exception as e:
        print('Oops something went wrong!')
        print(e)
