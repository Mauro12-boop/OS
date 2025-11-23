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


class Gym:
    def __init__(self):
        self.individual_spots = None
        self.trainers = None
        self.individual_lock = threading.RLock()
        self.trainer_lock = threading.RLock()

    def enter_individual(self, client):
        # Find free individual spot and mark it occupied
        with self.individual_lock:
            spot = None
            for s in self.individual_spots:
                if not s.is_occupied:
                    s.is_occupied = True
                    s.client = client
                    spot = s
                    break

        if spot:
            # LOG SUCCESS
            client.log_activity(
                amenity="gym",
                action="enter_individual",
                success=True,
                info=f"spot_{spot.id}"
            )

            spot.individual_session(client, spot.id)
            return

        # LOG FAILURE
        client.log_activity(
            amenity="gym",
            action="enter_individual",
            success=False,
            info="no_spots_available"
        )

        print(f"client {client.id} could not enter individual gym section as it is full.")

    def join_private_class(self, client):
        # Reserve a trainer atomically
        with self.trainer_lock:
            trainer = None
            for t in self.trainers:
                if t.is_available:
                    t.is_available = False
                    t.assigned_client = client
                    trainer = t
                    break

        if trainer is None:
            # LOG FAILURE
            client.log_activity(
                amenity="gym",
                action="private_class",
                success=False,
                info="no_trainer_available"
            )
            print(f"client {client.id} could not join private class as no trainers are available.")
            return

        # LOG SUCCESS
        client.log_activity(
            amenity="gym",
            action="private_class",
            success=True,
            info=f"trainer_{trainer.id}"
        )

        session = PrivateClassSession(5, client, trainer, self)
        session.start_session()


class IndividualSpot:
    def __init__(self, id, gym):
        self.id = id
        self.is_occupied = False
        self.client = None
        self.gym = gym

    def individual_session(self, client, spot_id):
        print(f"client {client.id} entered individual gym spot {spot_id}.")
        time.sleep(5)
        self.leave_individual(client, spot_id)

    def leave_individual(self, client, spot_id):
        with self.gym.individual_lock:
            self.is_occupied = False
            self.client = None
        print(f"client {client.id} left individual gym spot {spot_id}.")


class Trainer:
    def __init__(self, id):
        self.id = id
        self.is_available = True
        self.assigned_client = None


class PrivateClassSession:
    def __init__(self, duration, client, trainer, gym):
        self.duration = duration
        self.client = client
        self.trainer = trainer
        self.gym = gym

    def start_session(self):
        print(f"client {self.client.id} started a private class with trainer {self.trainer.id}.")
        time.sleep(self.duration)

        # Release trainer
        with self.gym.trainer_lock:
            self.trainer.is_available = True
            self.trainer.assigned_client = None

        print(f"client {self.client.id} finished private class with trainer {self.trainer.id}.")


def main():
    gym = Gym()

    # Create individual spots
    individual_spots = []
    for i in range(1, 20):
        individual_spots.append(IndividualSpot(i, gym))
    gym.individual_spots = individual_spots

    # Create trainers
    trainers = []
    for i in range(1, 4):
        trainers.append(Trainer(i))
    gym.trainers = trainers

    # Create clients
    clients = [Client(i) for i in range(1, 40)]

    def client_routine(client):
        coin = random.randint(1, 2)
        if coin == 1:
            gym.enter_individual(client)
        else:
            gym.join_private_class(client)

    # Start threads
    threads = []
    for c in clients:
        t = threading.Thread(target=client_routine, args=(c,))
        t.start()
        threads.append(t)

    # Wait for end
    for t in threads:
        t.join()

    # Print history
    for c in clients:
        print(f"\nClient {c.id} history:")
        for a in c.history["activities"]:
            print(a)


if __name__ == "__main__":
    main()