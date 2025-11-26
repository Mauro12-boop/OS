import random
import threading
import time

class EquestrianClub:
    def __init__(self):
        self.horses = []
        self.showjumping_tracks = None
        self.dressage_tracks = None
        self.horse_lock = threading.RLock()
        self.dressage_lock = threading.RLock()
        self.showjumping_lock = threading.RLock()

    def ride_horse(self, client):
        choice = random.randint(1, 2)
        if choice == 1:
            self.dressage_ride(client)
        else:
            self.showjumping_ride(client)

    def dressage_ride(self, client):
        horse = None
        track = None

        # ---------------- FIX 1 ----------------
        # If all tracks are full, track stays None. Must check immediately.
        # ----------------------------------------
        for i in self.dressage_tracks:
            with i.lock:
                if i.capacity < 3:
                    i.capacity += 1
                    i.clients.append(client)
                    track = i
                    break
        if track is None:  # FIX 1
            print(f'Client {client.id} could not find a dressage track')
            client.log_activity(
                amenity="Equestrian dressage",
                action="Ride Horse",
                success=False,
                info="No track available"
            )
            return

        # ---------------- FIX 2 ----------------
        # If no horse found, rollback track capacity
        # ----------------------------------------
        for h in self.horses:
            with h.lock:
                if not h.being_used:
                    h.being_used = True
                    h.assigned_client = client  # FIX 3: use consistent attribute
                    horse = h
                    track.horses.append(h)  # FIX 4: We must later remove this
                    break

        if horse is None:
            # ROLLBACK FIX
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

        # Same FIX as dressage
        for i in self.showjumping_tracks:
            with i.lock:
                if i.capacity < 3:
                    i.capacity += 1
                    i.clients.append(client)
                    track = i
                    break

        if track is None:  # FIX 1 again
            print(f'Client {client.id} could not find a showjumping track')
            client.log_activity(
                amenity="Equestrian Showjumping",
                action="Ride Horse",
                success=False,
                info="No track available"
            )
            return

        for h in self.horses:
            with h.lock:
                if not h.being_used:
                    h.being_used = True
                    h.assigned_client = client  # FIX consistent attribute
                    horse = h
                    track.horses.append(h)
                    break

        if horse is None:
            # ROLLBACK FIX
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
        self.id = id
        self.capacity = 0
        self.clients = []
        self.horses = []
        self.equestrianclub = equestrianclub
        self.lock = threading.RLock()

class Horse:
    def __init__(self, id):
        self.id = id
        self.being_used = False
        self.assigned_client = None  # FIX: use this consistently
        self.lock = threading.RLock()

class EquestrianSession:
    def __init__(self, id, track, client, horse):
        self.id = id
        self.track = track
        self.client = client
        self.horse = horse
        self.duration = 2  # seconds

    def start_dressage_session(self):
        type = "dressage"
        print(f'Client {self.client.id} has started a {type} session with horse {self.horse.id} in track {self.track.id}')
        time.sleep(self.duration)

        # -------------- FIX 5 ----------------
        # Remove horse from track.horses
        # Reset assigned_client
        # --------------------------------------
        with self.track.equestrianclub.dressage_lock:
            self.track.capacity -= 1
            self.track.clients.remove(self.client)
            self.track.horses.remove(self.horse)  # FIX
            self.horse.being_used = False
            self.horse.assigned_client = None     # FIX

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

        # SAME FIX AS ABOVE
        with self.track.equestrianclub.showjumping_lock:
            self.track.capacity -= 1
            self.track.clients.remove(self.client)
            self.track.horses.remove(self.horse)  # FIX
            self.horse.being_used = False
            self.horse.assigned_client = None     # FIX

        print(f'Client {self.client.id} has ended a {type} session with horse {self.horse.id} in track {self.track.id}')
        self.client.log_activity(
            amenity="Equestrian Showjumping",
            action="Ride Horse",
            success=True,
            info=f"Rode horse {self.horse.id}, Track {self.track.id}"
        )
