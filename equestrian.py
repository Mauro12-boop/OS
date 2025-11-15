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
        with self.dressage_lock:
            horse = None
            track = None
            for i in self.dressage_tracks:
                if i.capacity < 5:
                    i.capacity = i.capacity+1
                    i.clients.append(client)
                    track = i
                    break
            with self.horse_lock:
                for h in self.horses:
                    if not h.being_used:
                        h.being_used = True
                        h.client = client
                        horse = h
                        track.horses.append(h)
                        break

            if not horse or not track:
                print(f'Cliet {client.id} was not able to do an equestrian activity, no horse or track available')
                return

            if horse and track:
                practice =  EquestrianSession(random.randint(1,1000),track,client,horse)
                practice.start_dressage_session()
                return

    def showjumping_ride(self,client):
        with self.showjumping_lock:
            horse = None
            track = None
            for i in self.showjumping_tracks:
                if i.capacity < 5:
                    i.capacity = i.capacity+1
                    i.clients.append(client)
                    track = i
                    break
            with self.horse_lock:
                for h in self.horses:
                    if not h.being_used:
                        h.being_used = True
                        h.client = client
                        horse = h
                        track.horses.append(h)
                        break

            if not horse or not track:
                print(f'Cliet {client.id} was not able to do an equestrian activity, no horse or track available')
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

class Horse:
    def __init__(self,id):
        self.id = id
        self.being_used = False
        self.assigned_client = None


class EquestrianSession:
    def __init__(self, id,track, client,horse):
        self.id = id
        self.track = track
        self.client = client
        self.horse = horse
        self.duration = 5 #this will be in seconds, and 30 as if it was a 30 minutes massage


    def start_dressage_session(self):
        type = "dressage"
        print(f'Client {self.client.id} has started a {type} session with horse {self.horse.id} in track {self.track.id}')
        time.sleep(self.duration)
        with self.track.equestrianclub.dressage_lock:
            self.track.capacity = self.track.capacity-1
            self.track.clients.remove(self.client)
            self.horse.being_used = False
        print(f'Client {self.client.id} has ended a {type} session with horse {self.horse.id} in track {self.track.id}')


    def start_showjumping_session(self):
        type = "Show jumping"
        print(f'Client {self.client.id} has started a {type} session with horse {self.horse.id} in track {self.track.id}')
        time.sleep(self.duration)
        with self.track.equestrianclub.showjumping_lock:
            self.track.capacity = self.track.capacity-1
            self.track.clients.remove(self.client)
            self.horse.being_used = False
        print(f'Client {self.client.id} has ended a {type} session with horse {self.horse.id} in track {self.track.id}')



class Client:
    def __init__(self, id,equestrianclub):
        self.id = id
        self.equestrianclub = equestrianclub

    def go_equestrian(self):
        self.equestrianclub.ride_horse(self)



def main():
    equestrianclub = EquestrianClub()

    horses = []
    for i in range(1,12):
        horses.append(Horse(i))
    equestrianclub.horses = horses

    tracks_s = []
    for i in range(1,6):
        tracks_s.append(Tracks(i,equestrianclub))
    equestrianclub.showjumping_tracks = tracks_s

    tracks_d = []
    for i in range(7,12):
        tracks_d.append(Tracks(i,equestrianclub))
    equestrianclub.dressage_tracks = tracks_d


    clients = [Client(i, equestrianclub) for i in range(1, 20)]

    for i in clients:
        t = threading.Thread(target=i.go_equestrian)
        t.start()

if __name__ == "__main__":
    main()