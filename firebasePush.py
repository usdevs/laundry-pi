import time
import board
import busio
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

defaultThresholdValue = 1100
stateLighted = [False, False]
lightnessValue = [0, 0]

# Using guide from https://github.com/adafruit/Adafruit_CircuitPython_ADS1x15

# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create ADC object using I2C bus
ads = ADS.ADS1015(i2c)

# create single-ended input on channel 0
#chan = [AnalogIn(ads, ADS.P0), AnalogIn(ads, ADS.P1)]
#chan = [AnalogIn(ads, ADS.P1), AnalogIn(ads, ADS.P0)]
#print("{:>5}\t{:>5}".format('raw', 'v'))

cred = credentials.Certificate('./usc-laundry-test-firebase-adminsdk-0sph5-01054b85e5.json')

firebase_admin.initialize_app(cred)

db = firestore.client()

doc_ref = db.collection("test_collection").document("test_document")

generalThresholdValue = 1500

while True:
    lightnessValue0 = AnalogIn(ads, ADS.P0).value
    #lightnessValue1 = AnalogIn(ads, ADS.P1).value
    if lightnessValue0 < generalThresholdValue:
        machine0status = "on"
    else:
        machine0status = "off"
    #if lightnessValue1 > generalThresholdValue:
    #    machine1status = "on"
    #else:
    #    machine1status = "off"
    print("pin 0 " + str(lightnessValue0))
    #print("pin 1 " + str(lightnessValue1))
    doc_ref.set({
        "machine0":machine0status,
     #   "machine1":machine1status
    })
    time.sleep(0.1)

#LDR resistance decreases with increasing light intensity
#light on > lower ADC values

##doc_ref.set({
##    "test_value": "hello"
##    })
