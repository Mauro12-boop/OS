import random
import threading
import time


class Client:
    def __init__(self, id):
        self.id = id

        # One dictionary per client to store everything they did
        self.history = {
            "client_id": self.id,
            "activities": []   # list of activity dicts
        }

    def log_activity(self, amenity, action, success, info=""):
        """
        Store a single activity in the client's history.
        NO TIMESTAMP (simplified)
        """
        activity = {
            "amenity": amenity,
            "action": action,
            "success": int(success),  # 1 or 0
            "info": info
        }
        self.history["activities"].append(activity)


class Reception:
    def __init__(self):
        self.receptionists = None  # list
        self.reception_lock = threading.RLock()

    def request_assistance(self, client):

        # Reserve a receptionist
        with self.reception_lock:
            receptionist = None
            for r in self.receptionists:
                if r.is_available:
                    r.is_available = False
                    r.assigned_client = client
                    receptionist = r
                    break

        # FAILURE: No receptionist available
        if receptionist is None:
            print(f"client {client.id} could not be assisted at reception as no receptionists are available.")

            client.log_activity(
                amenity="reception",
                action="request_assistance",
                success=False,
                info="no_receptionist_available"
            )
            return

        # Pick request type
        request_type = random.choice(
            ["membership_update", "billing_question", "facility_booking", "general_info"]
        )

        durations = {
            "membership_update": 5,
            "billing_question": 6,
            "facility_booking": 4,
            "general_info": 3
        }

        duration = durations[request_type]

        # Start session
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
        print(
            f"client {self.client.id} is being assisted at reception by receptionist {self.receptionist.id} "
            f"for '{self.request_type}'."
        )
        time.sleep(self.duration)
        print(
            f"client {self.client.id} completed reception assistance '{self.request_type}' "
            f"with receptionist {self.receptionist.id}."
        )

        # LOG SUCCESS
        self.client.log_activity(
            amenity="reception",
            action=self.request_type,
            success=True,
            info=f"receptionist_{self.receptionist.id}"
        )

        self.finish_and_release_receptionist()

    def finish_and_release_receptionist(self):
        with self.reception.reception_lock:
            self.receptionist.is_available = True
            self.receptionist.assigned_client = None


def main():
    reception = Reception()

    # Create receptionists (critical resource)
    receptionists = []
    for i in range(1, 4):   # 3 receptionists
        receptionists.append(Receptionist(i))
    reception.receptionists = receptionists

    # Create clients
    clients = [Client(i) for i in range(1, 31)]

    def client_routine(client):
        reception.request_assistance(client)

    # Start threads
    threads = []
    for c in clients:
        t = threading.Thread(target=client_routine, args=(c,))
        t.start()
        threads.append(t)

    # Wait for completion
    for t in threads:
        t.join()

    for c in clients:
        print(f"\nClient {c.id} history:")
        for activity in c.history["activities"]:
            print(activity)


if __name__ == "__main__":
    main()