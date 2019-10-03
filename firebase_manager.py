import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from utils import sg_time_now

class FirebaseManager:
    
    def __init__(self, cert, pi_id):
        # setup database
        cred = credentials.Certificate(cert)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        self.pi_id = pi_id

        self.pi_status = db.collection('pi_status')
        self.laundry_status = db.collection('laundry_status')

    def init_pins(self, pins):
        for pin in pins:
            if not self.pin_exists(pin):
                self.create_pin(pin)

    def init_pi(self):
        if not self.pi_exists():
            self.create_pi()

    # Helper methods
    @staticmethod
    def _update_doc(doc, data):
        doc.update(data)
    
    @staticmethod
    def _doc_exists(doc):
        return doc.get().exists

    # Getting various documents
    def get_pin_doc(self, pin):
        return self.laundry_status.document(str(pin.id))

    def get_pi_doc(self):
        return self.pi_status.document(str(self.pi_id))

    def pin_exists(self, pin):
        return FirebaseManager._doc_exists(self.get_pin_doc(pin))

    def pi_exists(self):
        return FirebaseManager._doc_exists(self.get_pi_doc())

    # Writing to documents
    def create_pin(self, pin):
        now = sg_time_now()
        self.get_pin_doc(pin).set({
            'pinNo' : pin.id,
            'on' : pin.is_on(),
            'timeChanged' : now,
            'timeChangedCertain' : False,
        })

    def create_pi(self, description = ''):
        self.get_pi_doc().set({
            'piNo' : self.pi_id,
            'lastSeen' : sg_time_now(),
            'description' : description
        })

    def update_pin_on(self, pin, on, datetime, certain):
        FirebaseManager._update_doc(self.get_pin_doc(pin), {
            'on' : on,
            'timeChanged' : datetime,
            'timeChangedCertain' : certain
        })

    def update_pi_last_seen(self, datetime):
        FirebaseManager._update_doc(self.get_pi_doc(),
                         {'lastSeen' : datetime})

    # Reading from documents
    def read_pin(self, pin):
        """
        Returns None if the document for this pin does not exist.
        Note that dates return a google.api_core.datetime_helpers.DatetimeWithNanoseconds which extends from Python's datetime.datetime.
        """
        return self.get_pin_doc(pin).get().to_dict()

    def get_pi_last_seen(self):
        """
        Returns None if document for this pi does not exist.
        The date returned is a google.api_core.datetime_helpers.DatetimeWithNanoseconds which extends from Python's datetime.datetime.
        """
        return self.get_pi_doc().get().to_dict()['lastSeen']
