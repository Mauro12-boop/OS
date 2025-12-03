import random
import threading
import time

class Spa:
    def __init__(self):
        # Holds spa resources and locks for sauna/massage access
        self.massage_rooms = None
        self.masseuses = None
        self.saunas = None
        self.saunas_lock = threading.RLock()
        self.massage_lock = threading.RLock()

    def enter_sauna(self,client):
        # Tries to find an unoccupied sauna room
        with self.saunas_lock:
            sauna = None
            for i in self.saunas:
                if not i.is_occupied:
                    sauna = i
                    break
        if sauna:
            sauna.sauna_session(client,sauna.id)
            return
        # No sauna available
        print(f"client {client.id} could not enter sauna all of them were full")
        client.log_activity(
            amenity="Spa Sauna",
            action="Join Sauna",
            success=False,
            info=f"Could not join sauna"
        )
        return

    def do_massage(self,client):
        # Attempts to reserve both a room and a masseuse
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
                # Could not start massage session
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
        # Represents an employee who performs massages
        self.id = id
        self.is_available = True
        self.assigned_client = None

class MassageRoom:
    def __init__(self,id,spa):
        # Room state: occupancy and assigned client
        self.id = id
        self.is_occupied = False
        self.client = None
        self.masseuse = None
        self.spa = spa

class MassageSession:
    def __init__(self, id,room, client,masseuse):
        # Represents a single massage event
        self.id = id
        self.room = room
        self.client = client
        self.masseuse = masseuse
        self.duration = 5  # seconds representing a massage duration

    def start_session(self):
        # Runs the massage, then frees room and masseuse
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
        # Simple room with occupancy state
        self.id = id
        self.is_occupied = False
        self.client = None
        self.spa = spa

    def sauna_session(self, client, room):
        # Handles the sauna session lifecycle
        with self.spa.saunas_lock:
            self.is_occupied = True
            self.client = client
        print(f'client {self.client.id} has started a sauna session in sauna room {room}')
        time.sleep(5)
        self.leave_sauna(client, room)

    def leave_sauna(self,client,room):
        # Ends session and frees the sauna
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
