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

    def ride_horse(self,client):
        choice = random.randint(1,2)
        if choice == 1:
            self.dressage_ride(client)
        else:
            self.showjumping_ride(client)


    def dressage_ride(self,client):
        horse = None
        track = None
        for i in self.dressage_tracks:
            with i.lock:
                if i.capacity < 3:
                    i.capacity = i.capacity + 1
                    i.clients.append(client)
                    track = i
                    break

        for h in self.horses:
            with h.lock:
                if not h.being_used:
                    h.being_used = True
                    h.client = client
                    horse = h
                    track.horses.append(h)
                    break

        if not horse or not track:
            print(f'Cliet {client.id} was not able to do an equestrian activity, no horse or track available')
            client.log_activity(
                amenity="Equestrian dressage",
                action="Ride Horse",
                success=False,
                info="No horse or track available"
            )
            return

        practice = EquestrianSession(random.randint(1, 1000), track, client, horse)
        practice.start_dressage_session()
        return

    def showjumping_ride(self,client):
        horse = None
        track = None
        for i in self.showjumping_tracks:
            with i.lock:
                if i.capacity < 3:
                    i.capacity = i.capacity+1
                    i.clients.append(client)
                    track = i
                    break

        for h in self.horses:
            with h.lock:
                if not h.being_used:
                    h.being_used = True
                    h.client = client
                    horse = h
                    track.horses.append(h)
                    break

        if not horse or not track:
            print(f'Cliet {client.id} was not able to do an equestrian activity, no horse or track available')
            client.log_activity(
                amenity="Equestrian Showjumping",
                action="Ride Horse",
                success=False,
                info="No horse or track available"
            )
            return

        practice =  EquestrianSession(random.randint(1,1000),track,client,horse)
        practice.start_showjumping_session()
        return

class Tracks:
    def __init__(self,id,equestrianclub):
        self.id = id
        self.capacity = 0
        self.clients = []
        self.horses = []
        self.equestrianclub = equestrianclub
        self.lock = threading.RLock()

class Horse:
    def __init__(self,id):
        self.id = id
        self.being_used = False
        self.assigned_client = None
        self.lock = threading.RLock()


class EquestrianSession:
    def __init__(self, id,track, client,horse):
        self.id = id
        self.track = track
        self.client = client
        self.horse = horse
        self.duration = 2 #this will be in seconds, and 30 as if it was a 30 minutes massage


    def start_dressage_session(self):
        type = "dressage"
        print(f'Client {self.client.id} has started a {type} session with horse {self.horse.id} in track {self.track.id}')
        time.sleep(self.duration)
        with self.track.equestrianclub.dressage_lock:
            self.track.capacity = self.track.capacity-1
            self.track.clients.remove(self.client)
            self.horse.being_used = False
        print(f'Client {self.client.id} has ended a {type} session with horse {self.horse.id} in track {self.track.id}')
        self.client.log_activity(
            amenity="Equestrian dressage",
            action="Ride Horse",
            success=True,
            info=f"Rode horse {self.horse.id}, Track {self.track.id}"
        )
        return


    def start_showjumping_session(self):
        type = "Show jumping"
        print(f'Client {self.client.id} has started a {type} session with horse {self.horse.id} in track {self.track.id}')
        time.sleep(self.duration)
        with self.track.equestrianclub.showjumping_lock:
            self.track.capacity = self.track.capacity-1
            self.track.clients.remove(self.client)
            self.horse.being_used = False
        print(f'Client {self.client.id} has ended a {type} session with horse {self.horse.id} in track {self.track.id}')
        self.client.log_activity(
            amenity="Equestrian Showjumping",
            action="Ride Horse",
            success=True,
            info=f"Rode horse {self.horse.id}, Track {self.track.id}"
        )
        return