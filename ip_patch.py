import time
import socket

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

FIREBASE_CERT = './usc-laundry-test-firebase-adminsdk-0sph5-01054b85e5.json'
FIREBASE_COLLECTION = 'test_collection'
FIREBASE_DOCUMENT = 'test_document'

def run(cert=FIREBASE_CERT, collection=FIREBASE_COLLECTION, document=FIREBASE_DOCUMENT):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('8.8.8.8', 80))
            ip_address = s.getsockname()[0]

        update = dict()
        if ip_address not in ('127.0.0.1', ''):
            update.update({
                'HACK timestamp': time.strftime('%x %X'),
                'HACK ipaddress': ip_address,
            })

        if update:
            cred = credentials.Certificate(cert)
            firebase_admin.initialize_app(cred)
            db = firestore.client()
            doc = db.collection(collection).document(document)
            doc.set(update, merge=True)
            print('IP address uploaded to firebase!')
            print('> location:', collection,'/', document)

    except Exception as e:
        print('IP upload failed!')
        print(e)

if __name__ == '__main__':
    run()
