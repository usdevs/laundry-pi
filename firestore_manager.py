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
            # 'machines' : db.collection('machine_info'),
        }

        self._pi_doc = self._collections['pi'].document(str(self.pi_id))
        self._log = logging.getLogger()

    def init_pi(self):
        """Create a firestore document for this RPi in the pi_status collection if it doesn't
        already exist."""
        if not self._pi_doc.get().exists:
            self._pi_doc.set({'piNo' : self.pi_id})
            self.update_pi_last_seen()
            self._log.info("created piNo {} in firestore".format(self.pi_id))

    def init_pins(self, ids):
        """Creates a document in laundry_status for the pins with the given ids, if it doesn't
        already exist.

        Args:
            ids (iterable of strings): Pin IDs
        """
        for id in ids:
            doc = self._collections['current'].document(id)
            if not doc.get().exists:
                doc.set({
                    'pinId' : id,
                    'on' : False,
                    'timeChanged' : sg_time_now(),
                    'timeChangedCertain': False,
                    'piNo' : self.pi_id,
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
            id (string): Pin ID.
            on (bool): Whether the pin is on.
            timeChanged (datetime): Time of change/reading.
            timeChangedCertain (bool, optional): This should only be False for readings upon startup
                of the script. Defaults to True.
        """
        if type(id) != str:
            raise TypeError('id is {}, which is a {}. It should be an str.'.format(id,type(id)))
        if type(on) != bool:
            raise TypeError('on is {}, which is a {}. It should be a bool.'.format(on,type(on)))
        if type(timeChanged) != dt.datetime:
            raise TypeError('timeChanged is {}, which is a {}. It should be a datetime.'.format(timeChanged,type(timeChanged)))
        if type(timeChangedCertain) != bool:
            raise TypeError('timeChangedCertain is {}, which is a {}. It should be a bool'.format(timeChangedCertain, type(timeChangedCertain)))

        data = {
            'pinId' : id,
            'on' : on,
            'timeChanged' : timeChanged,
            'timeChangedCertain' : timeChangedCertain,
            'piNo' : self.pi_id,
        }
        self._collections['current'].document(id).update(data)
        self._collections['history'].add(data)

        self.update_pi_last_seen()

    def get_washing_machine_pin_ids(self):
        """Returns a list of pin IDs corresponding to washing machines."""
        washers = self._collections['current'].where('washer','==',True).get()
        ids = []
        for w in washers:
            ids.append(w.get('pinId'))
        return ids

    def get_pin_data(self, id):
        """Returns current pin status in a dict containing the pinId, on, time, timeChangedCertain.

        Args:
            id (string): Pin ID
        
        Returns:
            Dict of pinId (string), on (bool), timeChanged (datetime), timeChangedCertain (bool),
            plus whatever additional fields there are in firestore.
        """
        if type(id) != str:
            raise TypeError('id is {}, which is a {}. It should be an str.'.format(id,type(id)))

        data = self._collections['current'].document(id).get().to_dict()
        data['timeChanged'] = to_py_time(data['timeChanged'])
        return data

