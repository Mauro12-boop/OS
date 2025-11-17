import random
import threading
import time


class Reception:
    def __init__(self):
        self.receptionists = None #list
        self.reception_lock = threading.RLock()

    def request_assistance(self, client):
        with self.reception_lock: #reserve a receptionist
            receptionist = None
            for r in self.receptionists:
                if r.is_available:
                    r.is_available = False
                    r.assigned_client = client
                    receptionist = r
                    break

        if receptionist is None:
            print(f"client {client.id} could not be assisted at reception as no receptionists are available.")
            return

        #choose a request type
        request_type = random.choice(["membership_update", "billing_question", "facility_booking", "general_info"])
        durations = {
            "membership_update": 5,
            "billing_question": 6,
            "facility_booking": 4,
            "general_info": 3
        }
        duration = durations[request_type]

        #Start reception action
        session = ReceptionSession(duration, client, receptionist, request_type, self)
        session.start_session()


class Receptionist:
    def __init__(self, id):
        self.id = id
        self.is_available = True
        self.assigned_client = None


class ReceptionSession:
    def __init__(self, duration, client, receptionist, request_type, reception):
        self.duration = duration
        self.client = client
        self.receptionist = receptionist
        self.request_type = request_type
        self.reception = reception

    def start_session(self):
        print(f"client {self.client.id} is being assisted at reception by receptionist {self.receptionist.id} "
              f"for '{self.request_type}'.")
        time.sleep(self.duration)
        print(f"client {self.client.id} completed reception assistance '{self.request_type}' "
              f"with receptionist {self.receptionist.id}.")
        self.finish_and_release_receptionist()

    def finish_and_release_receptionist(self):
        with self.reception.reception_lock:
            self.receptionist.is_available = True
            self.receptionist.assigned_client = None


class Client:
    def __init__(self, id, reception):
        self.id = id
        self.reception = reception

    def goreception(self):
        self.reception.request_assistance(self)


def main():
    reception = Reception()

    #create receptionists, a critical resource
    receptionists = []
    for i in range(1, 4):
        receptionists.append(Receptionist(i))
    reception.receptionists = receptionists

    #create and start clients
    clients = [Client(i, reception) for i in range(1, 31)]
    for c in clients:
        t = threading.Thread(target=c.goreception)
        t.start()


if __name__ == "__main__":
    main()