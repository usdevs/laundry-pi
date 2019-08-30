import time
import board
import busio
import firebase_admin
import time
from firebase_admin import credentials
from firebase_admin import firestore
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Using guide from https://github.com/adafruit/Adafruit_CircuitPython_ADS1x15

# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create ADC object using I2C bus
ads1 = ADS.ADS1115(i2c, address=0x48)
ads2 = ADS.ADS1115(i2c, address=0x49)
ads3 = ADS.ADS1115(i2c, address=0x4a)
machineDict = {
    1 : (ads1, ADS.P0),
    2 : (ads1, ADS.P1),
    3 : (ads1, ADS.P2),
    2 : (ads1, ADS.P3),
    4 : (ads2, ADS.P0),
    5 : (ads2, ADS.P1),
    6 : (ads2, ADS.P2),
    7 : (ads2, ADS.P3),
    8 : (ads3, ADS.P0)
}


cred = credentials.Certificate('./usc-laundry-test-firebase-adminsdk-0sph5-01054b85e5.json')

firebase_admin.initialize_app(cred)

db = firestore.client()

doc_ref = db.collection("test_collection").document("test_document")

generalThresholdValue = 32000
machine0starttime = 0
machine0status = "off"

while True:
    for machineNumber in machineDict:
        lightnessValue = AnalogIn(machineDict[machineNumber][0], machineDict[machineNumber][1]).value
##    lightnessValue0 = AnalogIn(ads1, ADS.P0).value
    #lightnessValue1 = AnalogIn(ads, ADS.P1).value
##    if lightnessValue0 < generalThresholdValue:
##        if machine0status == "off":
##            machine0starttime = time.time()
##        machine0status = "on"
##    else:
##        if machine0status == "on":
##            machine0time = 0
##        machine0status = "off"
    #if lightnessValue1 > generalThresholdValue:
    #    machine1status = "on"
    #else:
    #    machine1status = "off"
    print("pin value is " + str(lightnessValue))
    #print("pin 1 " + str(lightnessValue1))
##    if machine0status == "on":
##        machine0TimeRemaining = time.time() - machine0starttime
##    else:
##        machine0TimeRemaining = 0
##    doc_ref.set({
##        "machine0":machine0status,
##        "machine0TimeRemaining":machine0TimeRemaining
##    })
    time.sleep(0.1)

#LDR resistance decreases with increasing light intensity
#light on > lower ADC values
