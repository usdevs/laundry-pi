import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from utils import sg_time_now, to_py_time
import datetime as dt
import logging

class FirestoreManager:

    def __init__(self, cert, pi_id):
        """
        Args:
            cert (str): Path to JSON file containing the Firestore certificate.
            pi_id (int): The unique ID to identify this RPi.

        Returns:
            A new FirestoreManager.
        """
        # setup database
        cred = credentials.Certificate(cert)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        self.pi_id = pi_id

        self._collections = {
            'pi' : db.collection('pi_status'),
            'history' : db.collection('laundry_status_history'),
            'current' : db.collection('laundry_status'),
            'machines' : db.collection('machine_info'),
        }

        self._pi_doc = self._collections['pi'].document(self.pi_id)
        self._log = logging.logger()

    def init_pi(self):
        """Create a firestore document for this RPi in the pi_status collection if it doesn't
        already exist."""
        if not self._pi_doc.get().exists():
            self._pi_doc.set({'piNo' : self.pi_id})
            self.update_pi_last_seen()
            self._log.info("created piNo {} in firestore".format(self.pi_id))

    def init_pins(self, ids):
        """Creates a document in laundry_status for the pins with the given ids, if it doesn't
        already exist.

        Args:
            ids (iterable of ints): Pin IDs
        """
        for id in ids:
            doc = self._collections['current'].document(id)
            if not doc.get().exists():
                doc.set({
                    'pinNo' : id,
                    'on' : False,
                    'timeChanged' : sg_time_now(),
                    'timeChangedCertain': False,
                })
            self._log.info("created pin no {} in firestore".format(id))

    def update_pi_last_seen(self):
        """Update the lastSeen time for this RPi to the current time."""
        now = sg_time_now()
        self._pi_doc.update({'lastSeen' : now })

    def update_pin(self, id, on, timeChanged, timeChangedCertain = True):
        """Add a new firestore document recording the current status (on/off) of a pin to the
        laundry_history collection. This should be done the script first starts or when the
        pin status changes.

        Args:
            id (int): Pin ID.
            on (bool): Whether the pin is on.
            timeChanged (datetime): Time of change/reading.
            timeChangedCertain (bool, optional): This should only be False for readings upon startup
                of the script. Defaults to True.
        """
        if type(id) != int:
            raise TypeError('id should be an int')
        if type(on) != bool:
            raise TypeError('on should be a bool')
        if type(timeChanged) != dt.datetime:
            raise TypeError('timeChanged should be a datetime')
        if type(timeChangedCertain) != bool:
            raise TypeError('timeChangedCertain should be a bool')

        data = {
            'pinNo' : id,
            'on' : on,
            'timeChanged' : time,
            'timeChangedCertain' : timeChangedCertain,
        }
        self._collections['current'].document(id).update(data)
        self._collections['history'].add(data)

        self.update_pi_last_seen()

    def get_washing_machine_pin_ids(self):
        """Returns a list of pin IDs corresponding to washing machines."""
        washers = self._collections['machines'].where('machineType','==','washer').stream()
        ids = list(map(washers, lambda w: int(w.to_dict()['pinNo'])))
        return ids

    def get_pin_data(self, id):
        """Returns current pin status in a dict containing the pinNo, on, time, timeChangedCertain.

        Args:
            id (int): Pin ID
        
        Returns:
            Dict of pinNo (int), on (bool), timeChanged (datetime), timeChangedCertain (bool).
        """
        data = self._collections['current'].document(id).get().to_dict()
        data['timeChanged'] = to_py_time(data['timeChanged'])
        return data

