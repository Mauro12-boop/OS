import threading
import time
import random
from collections import deque


class PadelCourtArea:
    def __init__(self, total_courts=4):
        self.total_courts = total_courts
        self.available_courts = total_courts

        # RLock allows the same thread to re-acquire the lock if needed
        self.court_lock = threading.RLock()

        # Queue for solo members who arrive without partners
        self.waiting_solo_players = deque()

        # Queue for groups (2–4 members arriving together)
        self.waiting_groups = deque()

        print(f"Padel Court Area initialized with {self.total_courts} courts")
        print(f"Available courts: {self.available_courts}\n")

    def handle_visitor_arrival(self, visitor_id, is_group=False, group_size=1):
        """
        Called whenever a club member (or group of members) arrives to use the padel amenity.
        """
        with self.court_lock:
            if is_group:
                # Create IDs for each member in the group (for logging / tracking)
                client_ids = [f"Member_{visitor_id}_{i + 1}" for i in range(group_size)]
                self._handle_group_arrival(client_ids)
            else:
                # Single member arrival
                self._handle_solo_arrival(f"Member_{visitor_id}")

    def _handle_solo_arrival(self, client_id):
        """
        Handle a solo member arrival.
        They either:
         - get paired with another solo member if one is waiting and a court is free, or
         - wait in the solo queue for a partner.
        """
        print(f" {client_id} arrived alone to play padel.")

        # If there's another solo already waiting AND a court is free, pair them
        if self.waiting_solo_players and self.available_courts > 0:
            partner_id = self.waiting_solo_players.popleft()
            clients = [partner_id, client_id]
            print(f" Solo player paired up! {partner_id} with {client_id}")
            self._start_padel_match(clients)
        else:
            # No partner or no court available → wait
            self.waiting_solo_players.append(client_id)
            print(f" {client_id} waits for a partner. Waiting solo players: {len(self.waiting_solo_players)}")

    def _handle_group_arrival(self, client_ids):
        """
        Handle a group arrival (2–4 members).
        If a court is free, they start playing immediately.
        Otherwise, they are queued as a group.
        """
        client_list = ", ".join(client_ids)
        print(f"Group arrives for padel: [{client_list}]")

        if self.available_courts > 0:
            # Immediate use of court
            self._start_padel_match(client_ids)
        else:
            # No courts → wait in group queue
            self.waiting_groups.append(client_ids)
            print(f" Group waits for court. Waiting groups: {len(self.waiting_groups)}")

    def _start_padel_match(self, client_ids):
        """
        Reserve a court and start a padel match in a new background thread.
        This models the 1-hour reservation period (simulated time).
        """
        # Reserve court
        self.available_courts -= 1
        court_number = self.total_courts - self.available_courts

        # 1 hour of play simulated as random seconds (e.g., between 10 and 20 seconds)
        # You can adjust this scale factor to represent "1 hour".
        match_duration = random.uniform(10, 20)

        clients_str = ", ".join(client_ids)
        print(f"Match STARTED on Padel Court {court_number}")
        print(f"Playing: [{clients_str}]")
        print(f"Available courts: {self.available_courts}/{self.total_courts}\n")

        # Create and start a background thread for the match
        threading.Thread(
            target=self._run_padel_match,
            args=(court_number, client_ids, match_duration),
            daemon=True  # daemon so it doesn't block program exit
        ).start()

    def _run_padel_match(self, court_number, client_ids, duration):
        """
        This function runs inside the match thread:
        simulates the 1-hour reservation by sleeping for 'duration',
        then frees up the court and assigns it to the next group/players in line.
        """
        # Simulate playing time
        time.sleep(duration)

        with self.court_lock:
            # Free the court
            self.available_courts += 1
            clients_str = ", ".join(client_ids)
            print(f"  Match COMPLETED on Padel Court {court_number}")
            print(f"  Finished: [{clients_str}]")
            print(f"  Now there are {self.available_courts}/{self.total_courts} available courts")

            # First, check if any groups are waiting for a court
            if self.waiting_groups:
                next_clients = self.waiting_groups.popleft()
                clients_str = ", ".join(next_clients)
                print(f"  Assigning Padel Court {court_number} to waiting group: [{clients_str}]")
                self._start_padel_match(next_clients)

            # If no groups, check if we can pair solo members
            elif len(self.waiting_solo_players) >= 2 and self.available_courts > 0:
                solo1 = self.waiting_solo_players.popleft()
                solo2 = self.waiting_solo_players.popleft()
                clients = [solo1, solo2]
                print(f"  Pairing {solo1} and {solo2} on Padel Court {court_number}")
                self._start_padel_match(clients)

    def get_court_status(self):
        """
        Return a snapshot of the current padel area status.
        Useful for final statistics / logging.
        """
        with self.court_lock:
            return {
                "available_courts": self.available_courts,
                "waiting_solo_players": len(self.waiting_solo_players),
                "waiting_groups": len(self.waiting_groups),
            }


def client_arrivals_padel(padel_court_area, simulation_duration=60):
    """
    Simulate the arrival of club members to the padel amenity.
    Members arrive randomly as solo players or groups over 'simulation_duration' seconds.
    """
    visitor_counter = 1
    start_time = time.time()

    print("Padel Area is OPEN!\n")

    # Generate arrivals for the duration of the simulation
    while time.time() - start_time < simulation_duration:
        # Random time between arrivals (1 to 8 seconds)
        time.sleep(random.randint(1, 8))

        # Decide if the arrival is a group or a solo member
        is_group = random.random() < 0.7  # 70% chance of a group

        if is_group:
            # Padel is usually doubles: 2 or 4 players
            group_size = random.choice([2, 4])
            padel_court_area.handle_visitor_arrival(
                visitor_counter,
                is_group=True,
                group_size=group_size
            )
        else:
            padel_court_area.handle_visitor_arrival(
                visitor_counter,
                is_group=False
            )

        visitor_counter += 1

    print("\nPadel Area is now CLOSED for new arrivals!")

    # After closing, we can still have ongoing matches; we just stop new arrivals.
    # Print final status snapshot
    final_status = padel_court_area.get_court_status()
    print("\nEnd-of-day summary:")
    print(f"   Available courts: {final_status['available_courts']}/{padel_court_area.total_courts}")
    print(f"   Solo players still waiting: {final_status['waiting_solo_players']}")
    print(f"   Groups still waiting: {final_status['waiting_groups']}")


def main():
    print("PADEL COURT SIMULATION (Country Club)")
    # Create padel court area with 4 courts
    padel_court_area = PadelCourtArea(total_courts=4)

    # Run the arrival simulation for N seconds
    # You can change 120 to simulate a busier/longer "day"
    client_arrivals_padel(padel_court_area, simulation_duration=120)

    # Extra sleep to let background matches finish before program exits
    # (since match threads are daemon threads)
    print("\nWaiting a bit for ongoing matches to complete...")
    time.sleep(30)
    print("Simulation finished.")


if __name__ == "__main__":
    main()