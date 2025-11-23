import random
import threading
import time

class Spa:
    def __init__(self):
        self.massage_rooms = None
        self.masseuses = None
        self.saunas = None
        self.saunas_lock = threading.RLock()
        self.massage_lock = threading.RLock()

    def enter_sauna(self,client):
        with self.saunas_lock:
            sauna = None
            for i in self.saunas:
                if not i.is_occupied:
                    sauna = i
                    break
        if sauna:
            sauna.sauna_session(client,sauna.id)
            return
        print(f"client {client.id} could not enter sauna all of them were full")
        client.log_activity(
            amenity="Spa Sauna",
            action="Join Sauna",
            success=False,
            info=f"Could not join sauna"
        )
        return

    def do_massage(self,client):
        with self.massage_lock:
            room = None
            masseuse = None

            for i in self.massage_rooms:
                if not i.is_occupied:
                    i.is_occupied = True
                    i.client = client
                    room = i
                    break

            for m in self.masseuses:
                if m.is_available == True:
                    m.is_available = False
                    masseuse = m
                    break

            if room is None or masseuse is None:
                print(f"client {client.id} could not start a massage — no room or masseuse available")
                client.log_activity(
                    amenity="Spa massage",
                    action="Join massage",
                    success=False,
                    info=f"Could not join massage"
                )
                return

        session = MassageSession(random.randint(1,1000),room,client,masseuse)
        session.start_session()

class Masseuse:
    def __init__(self,id):
        self.id = id
        self.is_available = True
        self.assigned_client = None

class MassageRoom:
    def __init__(self,id,spa):
        self.id = id
        self.is_occupied = False
        self.client = None
        self.masseuse = None
        self.spa = spa

class MassageSession:
    def __init__(self, id,room, client,masseuse):
        self.id = id
        self.room = room
        self.client = client
        self.masseuse = masseuse
        self.duration = 5 #this will be in seconds, and 30 as if it was a 30 minutes massage

    def start_session(self):
        print(f'client {self.client.id} has started a massage session with masseuse {self.masseuse.id} in room {self.room.id}')
        time.sleep(self.duration)
        with self.room.spa.massage_lock:
            self.room.is_occupied = False
            self.room.client = None
            self.masseuse.is_available = True
        print(f'client {self.client.id} has ended a massage session with masseuse {self.masseuse.id} in room {self.room.id}')
        self.client.log_activity(
            amenity="Spa massage",
            action="Join massage",
            success=True,
            info=f"masseuse {self.masseuse.id},room {self.room.id}"
        )
        return

class SaunaRoom:
    def __init__(self, id,spa):
        self.id = id
        self.is_occupied = False
        self.client = None
        self.spa = spa

    def sauna_session(self, client, room):
        with self.spa.saunas_lock:
            self.is_occupied = True
            self.client = client
        print(f'client {self.client.id} has started a sauna session in sauna room {room}')
        time.sleep(5)
        self.leave_sauna(client, room)

    def leave_sauna(self,client,room):
        with self.spa.saunas_lock:
            self.is_occupied = False
            self.client = None
        print(f'client {client.id} has ended a sauna session in sauna room {room}')
        client.log_activity(
            amenity="Spa sauna",
            action="Join sauna",
            success=True,
            info=f"Sauna room {room}"
        )
        return

class Client:
    def __init__(self, id,spa):
        self.id = id
        self.spa = spa

    def gotospa(self):
        coin = random.randint(1,2)
        if coin == 1:
            self.spa.enter_sauna(self)
        else:
            self.spa.do_massage(self)

def main():
    spa = Spa()

    saunas = []
    for i in range(1,6):
        saunas.append(SaunaRoom(i,spa))
    spa.saunas = saunas

    masseuses = []
    for i in range(1,6):
        masseuses.append(Masseuse(i))
    spa.masseuses = masseuses

    massageroomz = []
    for i in range(1,6):
        massageroomz.append(MassageRoom(i,spa))
    spa.massage_rooms = massageroomz

    clients = [Client(i, spa) for i in range(1, 40)]

    for i in clients:
        t = threading.Thread(target=i.gotospa)
        t.start()

if __name__ == "__main__":
    main()








