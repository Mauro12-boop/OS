import random
import threading
import time





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

