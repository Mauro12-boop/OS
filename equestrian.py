import random
import threading
import time

class EquestrianClub:
    def __init__(self):
        # Manages horses and both riding disciplines
        self.horses = []
        self.showjumping_tracks = None
        self.dressage_tracks = None
        self.horse_lock = threading.RLock()
        self.dressage_lock = threading.RLock()
        self.showjumping_lock = threading.RLock()

    def ride_horse(self, client):
        # Randomly selects between dressage and showjumping
        choice = random.randint(1, 2)
        if choice == 1:
            self.dressage_ride(client)
        else:
            self.showjumping_ride(client)

    def dressage_ride(self, client):
        horse = None
        track = None

        # Attempts to join a dressage track
        for i in self.dressage_tracks:
            with i.lock:
                if i.capacity < 3:
                    i.capacity += 1
                    i.clients.append(client)
                    track = i
                    break
        if track is None:
            print(f'Client {client.id} could not find a dressage track')
            client.log_activity(
                amenity="Equestrian dressage",
                action="Ride Horse",
                success=False,
                info="No track available"
            )
            return

        # Tries to assign an available horse
        for h in self.horses:
            with h.lock:
                if not h.being_used:
                    h.being_used = True
                    h.assigned_client = client
                    horse = h
                    track.horses.append(h)
                    break

        if horse is None:
            # Rollback if no horse was found
            with track.lock:
                track.capacity -= 1
                track.clients.remove(client)

            print(f'Client {client.id} could not find a horse for dressage')
            client.log_activity(
                amenity="Equestrian dressage",
                action="Ride Horse",
                success=False,
                info="No horse available"
            )
            return

        practice = EquestrianSession(random.randint(1, 1000), track, client, horse)
        practice.start_dressage_session()

    def showjumping_ride(self, client):
        horse = None
        track = None

        # Attempts to join a showjumping track
        for i in self.showjumping_tracks:
            with i.lock:
                if i.capacity < 3:
                    i.capacity += 1
                    i.clients.append(client)
                    track = i
                    break
        if track is None:
            print(f'Client {client.id} could not find a showjumping track')
            client.log_activity(
                amenity="Equestrian Showjumping",
                action="Ride Horse",
                success=False,
                info="No track available"
            )
            return

        # Attempts to assign a horse
        for h in self.horses:
            with h.lock:
                if not h.being_used:
                    h.being_used = True
                    h.assigned_client = client
                    horse = h
                    track.horses.append(h)
                    break

        if horse is None:
            # Rollback if no horse available
            with track.lock:
                track.capacity -= 1
                track.clients.remove(client)

            print(f'Client {client.id} could not find a horse for showjumping')
            client.log_activity(
                amenity="Equestrian Showjumping",
                action="Ride Horse",
                success=False,
                info="No horse available"
            )
            return

        practice = EquestrianSession(random.randint(1, 1000), track, client, horse)
        practice.start_showjumping_session()

class Tracks:
    def __init__(self, id, equestrianclub):
        # Represents a track for riding sessions
        self.id = id
        self.capacity = 0
        self.clients = []
        self.horses = []
        self.equestrianclub = equestrianclub
        self.lock = threading.RLock()

class Horse:
    def __init__(self, id):
        # Each horse tracks usage and assigned rider
        self.id = id
        self.being_used = False
        self.assigned_client = None
        self.lock = threading.RLock()

class EquestrianSession:
    def __init__(self, id, track, client, horse):
        # Manages a single riding session of either discipline
        self.id = id
        self.track = track
        self.client = client
        self.horse = horse
        self.duration = 2  # seconds

    def start_dressage_session(self):
        type = "dressage"
        print(f'Client {self.client.id} has started a {type} session with horse {self.horse.id} in track {self.track.id}')
        time.sleep(self.duration)

        # Ends session and frees resources
        with self.track.equestrianclub.dressage_lock:
            self.track.capacity -= 1
            self.track.clients.remove(self.client)
            self.track.horses.remove(self.horse)
            self.horse.being_used = False
            self.horse.assigned_client = None

        print(f'Client {self.client.id} has ended a {type} session with horse {self.horse.id} in track {self.track.id}')
        self.client.log_activity(
            amenity="Equestrian dressage",
            action="Ride Horse",
            success=True,
            info=f"Rode horse {self.horse.id}, Track {self.track.id}"
        )

    def start_showjumping_session(self):
        type = "Show jumping"
        print(f'Client {self.client.id} has started a {type} session with horse {self.horse.id} in track {self.track.id}')
        time.sleep(self.duration)

        # Ends session and resets track/horse state
        with self.track.equestrianclub.showjumping_lock:
            self.track.capacity -= 1
            self.track.clients.remove(self.client)
            self.track.horses.remove(self.horse)
            self.horse.being_used = False
            self.horse.assigned_client = None

        print(f'Client {self.client.id} has ended a {type} session with horse {self.horse.id} in track {self.track.id}')
        self.client.log_activity(
            amenity="Equestrian Showjumping",
            action="Ride Horse",
            success=True,
            info=f"Rode horse {self.horse.id}, Track {self.track.id}"
        )
