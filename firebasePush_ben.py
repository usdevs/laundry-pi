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
ads1 = ADS.ADS1115(i2c, address=0x49)
ads2 = ADS.ADS1115(i2c, address=0x48)
ads3 = ADS.ADS1115(i2c, address=0x4a)

# create single-ended input on channel 0
#chan = [AnalogIn(ads, ADS.P0), AnalogIn(ads, ADS.P1)]
#chan = [AnalogIn(ads, ADS.P1), AnalogIn(ads, ADS.P0)]
#print("{:>5}\t{:>5}".format('raw', 'v'))

cred = credentials.Certificate('./usc-laundry-test-firebase-adminsdk-0sph5-01054b85e5.json')

firebase_admin.initialize_app(cred)

db = firestore.client()

doc_ref = db.collection("test_collection").document("test_document")

generalThresholdValue = 32000

buses = [ads1, ads1, ads1, ads1, ads2, ads2, ads2, ads2, ads3]
ports = [ADS.P0, ADS.P1, ADS.P2, ADS.P3, ADS.P0, ADS.P1, ADS.P2, ADS.P3, ADS.P0]
machineCount = 9

machineStatuses = []
machineTimesLastStateChanged = []
lightValues = []
for i in list(range(machineCount)):
    machineStartTimes.append(0)
    machineStatuses.append("off")
    lightValues.append(0)
    machineTimesPassed.append(0)

while True:
    for i in list(range(machineCount)):
        lightValues[i] = AnalogIn(buses[i], ports[i]).value
        if lightValues[i] < generalThresholdValue:
            if machineStatuses[i] == "off":
                machineTimesLastStateChanged[i] = time.time()
            machineStatuses[i] = "on"
        else:
            if machineStatuses[i] == "on":
                machineTimesLastStateChanged[i] = 0
            machineStatuses[i] = "off"
        print("pin " + str(i) + ": " + str(lightValues[i]))

        if machineStatuses[i] == "on":
            machineTimesPassed[i] = time.time() - machineStartTimes[i]
        else:
            machineTimesPassed[i] = 0
        doc_ref.set({
            "machine" + str(i): machineStatuses[i],
            "machine" + str(i) + "TimePassed": machineTimesPassed[i]
        })
    time.sleep(0.1)
    # lightnessValue0 = AnalogIn(ads1, ADS.P0).value
    # #lightnessValue1 = AnalogIn(ads, ADS.P1).value
    # if lightnessValue0 < generalThresholdValue:
    #     if machine0status == "off":
    #         machine0starttime = time.time()
    #     machine0status = "on"
    # else:
    #     if machine0status == "on":
    #         machine0time = 0
    #     machine0status = "off"
    # #if lightnessValue1 > generalThresholdValue:
    # #    machine1status = "on"
    # #else:
    # #    machine1status = "off"
    # print("pin 0 " + str(lightnessValue0))
    # #print("pin 1 " + str(lightnessValue1))
    # if machine0status == "on":
    #     machine0TimeRemaining = time.time() - machine0starttime
    # else:
    #     machine0TimeRemaining = 0
    # doc_ref.set({
    #     "machine0":machine0status,
    #     "machine0TimeRemaining":machine0TimeRemaining
    # })
    

#LDR resistance decreases with increasing light intensity
#light on > lower ADC values
