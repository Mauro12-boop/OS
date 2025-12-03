import random
import threading
import time
from administrativeoffice import Reception, Receptionist, ReceptionSession
from equestrian import EquestrianClub,Tracks,Horse,EquestrianSession
from spa import Spa,Masseuse,MassageRoom,MassageSession,SaunaRoom
from soccer import SoccerPitch, Match
from gym import Gym,IndividualSpot,Trainer,PrivateClassSession
from cafeteria import Cafeteria,Server,FoodItem,ServingSession,EatingSession
from Golf import GolfCourse,Hole,Cart,GolfSession,RangeSlot
from swimming_pool import SwimmingPool
from bowling import SnackBar,BowlingAlley
from tennis import TennisCourt,TennisCourtArea
from Padel import PadelCourt,PadelCourtArea
from locker_room import LockerRoomArea
from coworking import Seat,QuietRoom,CoWorkingSpace
from database import init_db, save_all_histories


class SimulationSettings:
    def __init__(self):
        # Stores weather and simulation start time
        self.raining = random.choice([1,0])
        self.start_time = time.time()

class Client:
    def __init__(self, id, settings, alley=None, snack_bar=None):
        # Represents a single guest participating in the simulation
        self.id = id
        self.amenity_instance = None
        self.alley = alley
        self.snack_bar = snack_bar
        self.assigned = False
        self.finished_event = None
        self.golfcourse = None
        self.determination = random.random()
        self.reserved_room = None
        self.current_space = None
        self.settings = settings

        # Logs every action taken by the client
        self.history = {
            "client_id": self.id,
            "activities": []
        }

    def log_activity(self, amenity, action, success, info=""):
        # Saves client actions for database output
        activity = {
            "amenity": amenity,
            "action": action,
            "success": int(success),
            "info": info
        }
        self.history["activities"].append(activity)

    def random_selector(self, amenity_instances):
        # Main client loop: repeatedly picks a random amenity to visit
        self.golfcourse = amenity_instances[6]

        while time.time() - self.settings.start_time < 30:
            amenity_roulette = None

            # Raining changes amenity probabilities
            if self.settings.raining == 1:
                amenity_roulette = random.choice([1, 3, 5, 6, 8, 9, 12, 13])
            else:
                amenity_roulette = random.randint(1, 13)

            try:
                # Sequential amenity dispatching block
                if amenity_roulette == 1:
                    self.amenity_instance = amenity_instances[0]
                    self.amenity_instance.request_assistance(self)

                elif amenity_roulette == 2:
                    self.amenity_instance = amenity_instances[1]
                    self.amenity_instance.ride_horse(self)

                elif amenity_roulette == 3:
                    self.amenity_instance = amenity_instances[2]
                    coin = random.randint(1, 2)
                    if coin == 1:
                        self.amenity_instance.enter_sauna(self)
                    else:
                        self.amenity_instance.do_massage(self)

                elif amenity_roulette == 4:
                    self.amenity_instance = amenity_instances[3]
                    self.amenity_instance.join_a_team(self)
                    if self in self.amenity_instance.teamA:
                        self.amenity_instance.start_match()

                elif amenity_roulette == 5:
                    self.amenity_instance = amenity_instances[4]
                    coin = random.randint(1, 2)
                    if coin == 1:
                        self.amenity_instance.enter_individual(self)
                    else:
                        self.amenity_instance.join_private_class(self)

                elif amenity_roulette == 6:
                    self.amenity_instance = amenity_instances[5]
                    self.amenity_instance.order_at_counter(self)

                elif amenity_roulette == 7:
                    self.amenity_instance = amenity_instances[6]
                    time.sleep(random.uniform(0.1, 1.0))
                    coin = random.randint(1, 2)
                    if coin == 1:
                        self.amenity_instance.practice_range(self)
                    else:
                        self.amenity_instance.play_course(self)

                elif amenity_roulette == 8:
                    determination = random.random()
                    self.amenity_instance = amenity_instances[7]
                    first_choice = random.randint(1, 2)

                    # Swimming pool decision logic
                    if first_choice == 1:
                        success = self.amenity_instance.enter_lane_pool(self)
                        if not success:
                            print(f"client {self.id} found lane pool full")
                            success = self.amenity_instance.enter_recreation_pool(self)
                            if not success:
                                print(f"client {self.id} found both pools full")
                                if determination > 0.5:
                                    queue_choice = random.randint(1, 2)
                                    if queue_choice == 1:
                                        self.amenity_instance.join_lanes_queue(self)
                                    else:
                                        self.amenity_instance.join_recreation_queue(self)
                                else:
                                    print(f"client {self.id} decided to leave - not determined enough")
                            else:
                                print(f"client {self.id} successfully entered recreation pool")
                        else:
                            print(f"client {self.id} successfully entered lane pool")
                    else:
                        success = self.amenity_instance.enter_recreation_pool(self)
                        if not success:
                            print(f"client {self.id} found recreation pool full")
                            success = self.amenity_instance.enter_lane_pool(self)
                            if not success:
                                print(f"client {self.id} found both pools full")
                                if determination > 0.5:
                                    queue_choice = random.randint(1, 2)
                                    if queue_choice == 1:
                                        self.amenity_instance.join_lanes_queue(self)
                                    else:
                                        self.amenity_instance.join_recreation_queue(self)
                                else:
                                    print(f"client {self.id} decided to leave - not determined enough")
                            else:
                                print(f"client {self.id} successfully entered lane pool")
                        else:
                            print(f"client {self.id} successfully entered recreation pool")

                elif amenity_roulette == 9:
                    self.amenity_instance = amenity_instances[8]
                    purchase_timing = random.choice(["none", "before", "after"])
                    if purchase_timing == "before":
                        self.amenity_instance[1].purchase(self)

                    self.amenity_instance[0].request_lane(self)

                    if purchase_timing == "after":
                        self.amenity_instance[1].purchase(self)

                elif amenity_roulette == 10:
                    self.amenity_instance = amenity_instances[9]
                    self.amenity_instance.play_tennis(self)

                elif amenity_roulette == 11:
                    self.amenity_instance = amenity_instances[10]
                    self.amenity_instance.play_padel(self)

                elif amenity_roulette == 12:
                    gender = random.choice(["Male", "Female"])
                    wants_shower = random.random() < 0.7
                    if gender == "Male":
                        self.amenity_instance = amenity_instances[11][0]
                    else:
                        self.amenity_instance = amenity_instances[11][1]
                    self.amenity_instance.use_locker_room(self, gender, wants_shower)

                elif amenity_roulette == 13:
                    self.amenity_instance = amenity_instances[12]
                    self.amenity_instance.allocate_space(self)
                    time.sleep(random.randint(1, 2))
                    self.amenity_instance.leave_space(self)

            except Exception as e:
                # Ensures the simulation keeps running even if an amenity fails
                print(f"Client {self.id} encountered an error in amenity {amenity_roulette}: {e}")

            time.sleep(5)

        return


def main():
    # Global initialization of all amenities and resources
    settings = SimulationSettings()
    if settings.raining == 1:
        print("Today it is raining")
        client_num = 50
    else:
        print("Today it is not raining")

    # Reception setup
    reception = Reception()
    receptionists = []
    for i in range(1, 4):
        receptionists.append(Receptionist(i))
    reception.receptionists = receptionists

    # Equestrian setup
    equestrianclub = EquestrianClub()

    horses = []
    for i in range(1, 12):
        horses.append(Horse(i))
    equestrianclub.horses = horses

    tracks_s = []
    for i in range(1, 6):
        tracks_s.append(Tracks(i, equestrianclub))
    equestrianclub.showjumping_tracks = tracks_s

    tracks_d = []
    for i in range(7, 12):
        tracks_d.append(Tracks(i, equestrianclub))
    equestrianclub.dressage_tracks = tracks_d

    # Spa setup
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

    # Soccer
    soccerpitch = SoccerPitch()

    # Gym
    gym = Gym()

    individual_spots = []
    for i in range(1, 20):
        individual_spots.append(IndividualSpot(i, gym))
    gym.individual_spots = individual_spots

    trainers = []
    for i in range(1, 4):
        trainers.append(Trainer(i))
    gym.trainers = trainers

    # Cafeteria
    cafeteria = Cafeteria()
    servers = []
    for i in range(1, 4):
        servers.append(Server(i))
    cafeteria.servers = servers
    cafeteria.menu = [
        FoodItem("sandwich", 10),
        FoodItem("salad", 8),
        FoodItem("pizza", 6),
        FoodItem("pasta", 5),
    ]

    # Golf
    golfcourse = GolfCourse()
    holes = [Hole(i, golfcourse) for i in range(1, 10)]
    golfcourse.holes = holes
    carts = [Cart(i) for i in range(1, 6)]
    golfcourse.carts = carts
    range_slots = [RangeSlot(i, golfcourse) for i in range(1, 6)]
    golfcourse.range_slots = range_slots

    # Swimming pool
    pool = SwimmingPool()

    # Bowling setup
    alley = BowlingAlley(num_lanes=10)
    snack_bar = SnackBar()

    # Tennis
    tennis = TennisCourtArea(total_courts=4)

    # Padel
    padel = PadelCourtArea(total_courts=4)

    # Locker rooms
    male_locker_room = LockerRoomArea("Male", total_lockers=8, total_showers=3)
    female_locker_room = LockerRoomArea("Female", total_lockers=8, total_showers=3)

    # Coworking
    coworking = CoWorkingSpace()

    # Database initialization
    init_db()

    # Amenity registry
    amenity_instances = [
        reception, equestrianclub, spa, soccerpitch, gym, cafeteria,
        golfcourse, pool, [alley, snack_bar], tennis, padel,
        [male_locker_room, female_locker_room], coworking
    ]

    # Create clients
    clients = [Client(i,settings=settings) for i in range(1, 100)]

    # Preassign reserved coworking rooms
    reserved_clients = 4
    reserved_clients = min(reserved_clients, len(coworking.quiet_rooms))

    for i in range(reserved_clients):
        room_obj = coworking.quiet_rooms[i]
        room_obj.reserved_by = i + 1
        clients[i].reserved_room = room_obj

    # Start clients
    for c in clients:
        t = threading.Thread(target=c.random_selector, args=(amenity_instances,))
        t.start()
        time.sleep(0.1)

    # Wait for all threads to finish
    for thread in threading.enumerate():
        if thread is not threading.main_thread():
            thread.join()

    # Final database save
    save_all_histories(clients)


if __name__ == "__main__":
    main()
