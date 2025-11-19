import threading
import time
import random
from collections import deque


class TennisCourtArea:
    def _init_(self, total_courts=4):
        self.total_courts = total_courts
        self.available_courts = total_courts
        self.court_lock = threading.RLock()
        self.waiting_solo_players = deque() # for those that don't have a group to play
        self.waiting_groups = deque() # supports thead-safe memory efficient operations
        print(f"Tennis Court Area initialized with {self.total_courts} courts")
        print(f"Available courts: {self.available_courts}\n")
    def handle_visitor_arrival(self, visitor_id, is_group=False, group_size=1):
        with self.court_lock: # when there is someone
            if is_group:
                client_ids = [f"Client_{visitor_id}_{i + 1}" for i in range(group_size)] # to change to be aligned with the client base_id
                self._handle_group_arrival(client_ids)
            else:
                self.handle_solo_arrival(f"Client{visitor_id}")

    def _handle_solo_arrival(self, client_id): # if the person arrives solo
        print(f" The {client_id} arrived alone")
        if self.waiting_solo_players and self.available_courts > 0: # Check if there's another solo waiting and courts available
            partner_id = self.waiting_solo_players.popleft() # then we take and match those that are alone
            clients = [partner_id, client_id]
            print(f" Solo player paired up! {partner_id} with {client_id}")
            self._start_tennis_match(clients)
        else: # if there is no other solo player then waits in a queue
            self.waiting_solo_players.append(client_id)
            print(f" {client_id} waits for partner. Waiting solo players: {len(self.waiting_solo_players)}")

    def _handle_group_arrival(self, client_ids): # Now when we have a group
        client_list = ", ".join(client_ids)
        print(f"Clients arrive: [{client_list}]")
        if self.available_courts > 0: # if there is a court available then they will immediately start
            self._start_tennis_match(client_ids)
        else: # If there are no courts available, wait in group queue until one becomes free
            self.waiting_groups.append(client_ids)
            print(f"Group waits for court. Waiting groups: {len(self.waiting_groups)}")

    def _start_tennis_match(self, client_ids): # once in the court
        # RLOCK -- reentrant acquisition by same thread
        self.available_courts -= 1
        court_number = self.total_courts - self.available_courts
        match_duration = random.uniform(5, 15) # random time of match

        # the display for the user:
        clients_str = ", ".join(client_ids)
        print(f"Match STARTED on Court {court_number}")
        print(f"Playing: [{clients_str}]")
        print(f"Available courts: {self.available_courts}/{self.total_courts}\n")

# BASED ON RESEARCH: thus creates and starts a new background thread to run the tennis match
        threading.Thread( # new object
            target=self._run_tennis_match, # tells thread what function to run when it starts
            args=(court_number, client_ids, match_duration), # gives arguments the inputs
            daemon=True # so that it runs in the background and no blocking of the main program
        ).start() # the daemon is good so that we don't have to manually stop every time

    def _run_tennis_match(self, court_number, client_ids, duration): #the users are playing here
        time.sleep(duration)
        with self.court_lock:
            self.available_courts += 1
            clients_str = ", ".join(client_ids)
            print(f"  Match COMPLETED on Court {court_number}")
            print(f"  Finished: [{clients_str}]")
            print(f"  Now there are  {self.available_courts}/{self.total_courts} available courts")

            if self.waiting_groups: # check if groups are waiting
                next_clients = self.waiting_groups.popleft()
                clients_str = ", ".join(next_clients)
                print(f" Assigning Court {court_number} to waiting clients: [{clients_str}]")
                self._start_tennis_match(next_clients)

            elif len(self.waiting_solo_players) >= 2 and self.available_courts > 0: #then we check if solos can be paired up
                solo1 = self.waiting_solo_players.popleft()
                solo2 = self.waiting_solo_players.popleft()
                clients = [solo1, solo2]
                print(f"Pairing {solo1} and {solo2} on Court {court_number}")
                self._start_tennis_match(clients)

    def get_court_status(self):
        with self.court_lock:
            return {
                'available_courts': self.available_courts,
                'waiting_solo_players': len(self.waiting_solo_players),
                'waiting_groups': len(self.waiting_groups)
            }
def client_arrivals_tennis(tennis_court_area, simulation_duration=30):
    visitor_counter = 1
    start_time = time.time()

    print("Tennis Area is Open!\n")

# THIS IS TO STIMULATE THEIR ARRIVALS SUBJECT TO CHANGE
    while time.time() - start_time < simulation_duration:
        time.sleep(random.randint(1, 10))
        is_group = random.random() < 0.7  # 70% chance of a group
### how to make this be like as outside and the club members arrive to the tennis and then it classifies if solo or grouo###
        if is_group:
            group_size = random.randint(2, 4)
            tennis_court_area.handle_visitor_arrival(visitor_counter, is_group=True, group_size=group_size)
        else:
            tennis_court_area.handle_visitor_arrival(visitor_counter, is_group=False)
        visitor_counter += 1

    print(f"\n Tennis area is now closed!")

    # Print final status
    final_status = tennis_court_area.get_court_status()
    print(f"\n From the day:")
    print(f"   Available courts: {final_status['available_courts']}/{tennis_court_area.total_courts}")
    print(f"   Solo players still waiting: {final_status['waiting_solo_players']}")
    print(f"   Groups still waiting: {final_status['waiting_groups']}")


def main():

    print("TENNIS COURT SIMULATION")
    tennis_court_area = TennisCourtArea(total_courts=4)  # Create tennis court area with 4 courts
    client_arrivals_tennis(tennis_court_area, simulation_duration=240) # TO BE CHANGED

if __name__ == "__main__":
    main()