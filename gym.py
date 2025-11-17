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
        #Find free individual spot and mark it occupied
        with self.individual_lock:
            spot = None
            for s in self.individual_spots:
                if not s.is_occupied:
                    s.is_occupied = True
                    s.client = client
                    spot = s
                    break

        if spot:
            spot.individual_session(client, spot.id)
            return
        print(f"client {client.id} could not enter individual gym section as it is full.")

    def join_private_class(self, client):
        #Reserve a trainer atomically (like picking a Masseuse, but without a room)
        with self.trainer_lock:
            trainer = None
            for t in self.trainers:
                if t.is_available:
                    t.is_available = False
                    t.assigned_client = client
                    trainer = t
                    break

        if trainer is None:
            print(f"client {client.id} could not join private class as no trainers are available.")
            return

        #Start a private class session
        session = PrivateClassSession(5, client, trainer, self)
        session.start_session()


class IndividualSpot:
    def __init__(self, id, gym):
        self.id = id
        self.is_occupied = False
        self.client = None
        self.gym = gym

    def individual_session(self, client, spot_id):
        #Log start, simulate time, then leave
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
        with self.gym.trainer_lock:
            self.trainer.is_available = True
            self.trainer.assigned_client = None
        print(f"client {self.client.id} finished private class with trainer {self.trainer.id}.")


class Client:
    def __init__(self, id, gym):
        self.id = id
        self.gym = gym

    def gogym(self):
        coin = random.randint(1, 2)
        if coin == 1:
            self.gym.enter_individual(self)
        else:
            self.gym.join_private_class(self)


def main():
    gym = Gym()

    individual_spots = []
    for i in range(1, 20):
        individual_spots.append(IndividualSpot(i, gym))
    gym.individual_spots = individual_spots

    trainers = []
    for i in range(1, 4):
        trainers.append(Trainer(i))
    gym.trainers = trainers

    clients = [Client(i, gym) for i in range(1, 40)] #to be chnaged

    for i in clients:
        t = threading.Thread(target=i.gogym)
        t.start()

if __name__ == "__main__":
    main()
