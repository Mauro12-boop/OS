import random
import threading
import time


class Client:
    def __init__(self, id, alley=None, snack_bar=None):
        self.id = id
        self.alley = alley
        self.snack_bar = snack_bar
        self.assigned = False
        self.finished_event = None


        # One dictionary per client to store everything they did
        self.history = {
            "client_id": self.id,
            "activities": []  # list of activity dicts
        }

    def log_activity(self, amenity, action, success, info=""):

        activity = {
            "amenity": amenity,
            "action": action,
            "success": int(success),  # 1 or 0 (SQLite-friendly)
            "info": info
        }
        self.history["activities"].append(activity)



    def random_selector(self,amenity_instances):
        amenity_roulette = random.randint(1,1)
        #addd loop so that it runs forever
        if amenity_roulette ==1:
            self.amenity_instance = amenity_instances[0]
            self.amenity_instance.request_assistance(self)
        elif amenity_roulette ==2:
            self.amenity_instance = amenity_instances[1]
            self.amenity_instance.ride_horse(self)
        elif amenity_roulette ==3:
            self.amenity_instance = amenity_instances[2]
            coin = random.randint(1, 2)
            if coin == 1:
                self.amenity_instance.enter_sauna(self)
            else:
                self.amenity_instance.do_massage(self)
        elif amenity_roulette ==4:
            self.amenity_instance = amenity_instances[3]
            self.amenity_instance.join_a_team(self)
            self.amenity_instance.start_match()
        elif amenity_roulette ==5:
            self.amenity_instance = amenity_instances[4]
            coin = random.randint(1, 2)
            if coin == 1:
                self.amenity_instance.enter_individual(self)
            else:
                self.amenity_instance.join_private_class(self)
        elif amenity_roulette ==6:
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
            determination = determination = random.random()
            self.amenity_instance = amenity_instances[7]
            first_choice = random.randint(1, 2)
            # lane pool = 1 and recreation = 2
            if first_choice == 1:
                success = self.amenity_instance.enter_lane_pool(self)
                if not success:
                    print(f"client {self.id} found lane pool full")
                    # Try recreation pool
                    success = self.amenity_instance.enter_recreation_pool(self)
                    if not success:
                        print(f"client {self.id} found both pools full")
                        # Decide whether to wait in queue or leave
                        if determination > 0.5:  # Really wants to swim
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
                # Try recreation pool first
                success = self.amenity_instance.enter_recreation_pool(self)
                if not success:
                    print(f"client {self.id} found recreation pool full")
                    # Try lane pool
                    success = self.amenity_instance.enter_lane_pool(self)
                    if not success:
                        print(f"client {self.id} found both pools full")
                        # Decide whether to wait in queue or leave
                        if determination > 0.5:  # Really wants to swim
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
                # Buy a snack before bowling
                self.amenity_instance[1].purchase(self.id)

            # Request a lane (this may block until a lane/group is available)
            self.amenity_instance[0].request_lane(self)  # <-- ALWAYS runs (outside the ifs)

            if purchase_timing == "after":
                # Buy a snack after finishing bowling
                self.amenity_instance[1].purchase(self.id)
        elif amenity_roulette == 10:
            pass






def main():

    #Creating instances of Necessary objects

    #Reception
    reception = Reception()
    receptionists = []
    for i in range(1, 4):
        receptionists.append(Receptionist(i))
    reception.receptionists = receptionists

    #Equestrian
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

    #spa
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

    #soccer

    soccerpitch = SoccerPitch()

    #Gym

    gym = Gym()

    individual_spots = []
    for i in range(1, 20):
        individual_spots.append(IndividualSpot(i, gym))
    gym.individual_spots = individual_spots

    trainers = []
    for i in range(1, 4):
        trainers.append(Trainer(i))
    gym.trainers = trainers

    #Cafeteria

    cafeteria = Cafeteria()
    servers = []  # create servers (critical resource)
    for i in range(1, 4):  # 3 servers
        servers.append(Server(i))
    cafeteria.servers = servers
    cafeteria.menu = [ # menu with limited stock (critical resource)
        FoodItem("sandwich", 10),
        FoodItem("salad", 8),
        FoodItem("pizza", 6),
        FoodItem("pasta", 5),
    ]

    #Golf

    golfcourse = GolfCourse()
    holes = [Hole(i, golfcourse) for i in range(1, 10)] #Create 9 holes (typical golf course may have 9 or 18 holes)
    golfcourse.holes = holes
    carts = [Cart(i) for i in range(1, 6)] # Create 5 golf carts (limited number of carts available)
    golfcourse.carts = carts
    range_slots = [RangeSlot(i, golfcourse) for i in range(1, 6)] #Create 5 driving range slots for practice at the driving range
    golfcourse.range_slots = range_slots

    #swimming pool
    pool = SwimmingPool()

    #bowling
    alley = BowlingAlley(num_lanes=10)
    snack_bar = SnackBar()

    #Compilation of all amenities created
    amenity_instances = [reception,equestrianclub,spa,soccerpitch,gym,cafeteria,golfcourse,pool,[alley,snack_bar]]

    # create and start clients
    clients = [Client(i) for i in range(1, 300)]
    for c in clients:
        t = threading.Thread(target=c.random_selector, args = (amenity_instances,) )
        t.start()
        time.sleep(0.1)


if __name__ == "__main__":
    main()