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

    def add_machine(self, machine):
        self.machines.append(machine)

    def run(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.main())

    async def push(self, data):
        self.db.set(data, merge=True)

    async def main(self):
        while True:
            status = list()
            await asyncio.gather(*(machine.write_status(status) for machine in self.machines))
            await asyncio.gather(*(self.push(data) for data in status))
            await asyncio.sleep(self.interval)

class LaundryMachine:
    def __init__(self, name, sensor):
        self.name = name
        self.running = None

    async def write_status(self, record):
        running = await self.sensor.status()
        if running != self.running:
            self.running = running
            record.append({
                f'{self.name}_running': self.running,
                f'{self.name}_time': time.time(),
            })

    async def update_status(self):
        """Update self.running and self.start_time"""
        raise NotImplementedError('Machine should be subclassed')

class ADS1x15:
    def __init__(self, ads):
        self.ads = ads

    async def status(self):
        lightness = AnalogIn(self.ads, ADS.P0).value
        return lightness < THRESHHOLD

if __name__ == '__main__':
    # Initialize firebase
    fb = FirebaseManager(CERT_PATH, interval=0.5)

    # Create the I2C bus
    i2c = busio.I2C(board.SCL, board.SDA)

    # Create ADC object using I2C bus
    ads_inputs = [
        ADS.ADS1115(i2c, address=0x49),
        ADS.ADS1115(i2c, address=0x48),
        ADS.ADS1115(i2c, address=0x4a),
    ]

    # Wrap ADCs in an interface before passing to firebase Object
    machines = [LaundryMachine(ADS1x15(input)) for input in ads_inputs]
    for machine in machines:
        fb.add_machine(machine)

    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(fb.run())

    except Exception as e:
        loop.stop()
        print(e)
        input()
