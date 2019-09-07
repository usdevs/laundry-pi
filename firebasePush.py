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
    4 : (ads1, ADS.P3),
    5 : (ads2, ADS.P0),
    6 : (ads2, ADS.P1),
    7 : (ads2, ADS.P2),
    8 : (ads2, ADS.P3),
    9 : (ads3, ADS.P0)
}

machineTypeDict = {
    1 : "dryer",
    2 : "dryer",
    3 : "dryer",
    4 : "dryer",
    5 : "washing",
    6 : "washing",
    7 : "washing",
    8 : "washing",
    9 : "washing",
}

machineConnectedDict = {
    1 : False,
    2 : True,
    3 : True,
    4 : False,
    5 : True,
    6 : True,
    7 : False,
    8 : False,
    9 : True,
}

machineStatusDict = {
    1 : "off",
    2 : "off",
    3 : "off",
    4 : "off",
    5 : "off",
    6 : "off",
    7 : "off",
    8 : "off",
    9 : "off",
}

machineStartTimeDict = {
    1 : 0,
    2 : 0,
    3 : 0,
    4 : 0,
    5 : 0,
    6 : 0,
    7 : 0,
    8 : 0,
    9 : 0,
}

cred = credentials.Certificate('./usc-laundry-test-firebase-adminsdk-0sph5-01054b85e5.json')

firebase_admin.initialize_app(cred)
db = firestore.client()
doc_ref = db.collection("test_collection").document("test_document")

generalThresholdValue = 32000
totalCycleTimeWashing = 1800
totalCycleTimeDryer = 2700

# sends the Pi's IP address to the firebase server
# import ip_patch
# ip_patch.run()

while True:

    # ping the pi
    doc_ref.set({
        "pi_1_last_seen" : time.strftime('%x %X'),
    }, merge=True)

    for machineNumber in machineDict:
        if machineConnectedDict[machineNumber] == False:
            continue
        lightnessValue = AnalogIn(machineDict[machineNumber][0], machineDict[machineNumber][1]).value
        if lightnessValue < generalThresholdValue:
            if machineStatusDict[machineNumber] == "off":
                machineStartTimeDict[machineNumber] = time.time()
            machineStatusDict[machineNumber] = "on"
        else:
            if machineStatusDict[machineNumber] == "on":
                machineStartTimeDict[machineNumber] = 0
            machineStatusDict[machineNumber] = "off"
        print("pin value for machine " + str(machineNumber) + " is " + str(lightnessValue) + ", status is " + str(machineStatusDict[machineNumber]))
        if machineStatusDict[machineNumber] == "on":
            machineTimeElapsed = time.time() - machineStartTimeDict[machineNumber]
            if machineTypeDict[machineNumber] == "dryer":
                machineTimeRemaining = totalCycleTimeDryer - machineTimeElapsed
            else:
                machineTimeRemaining = totalCycleTimeWashing - machineTimeElapsed
        else:
            machineTimeRemaining = 0
        doc_ref.set({
            "machine" + str(machineNumber):machineStatusDict[machineNumber],
            "machine" + str(machineNumber) + "TimeRemaining":machineTimeRemaining
        },merge=True)

        time.sleep(0.1)

#LDR resistance decreases with increasing light intensity
#light on > lower ADC values
