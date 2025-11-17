import threading
import time
import random

# Snack bar with a list of items and thread-safe revenue tracking
class SnackBar:
    def __init__(self):
        self.items = [
            ("Burger", 8.5),
            ("Hot Dog", 5.0),
            ("Nachos", 6.0),
            ("Soda", 2.5),
            ("Water", 1.5),
            ("Coffee", 3.0),
            ("Fries", 3.5),
            ("Pizza Slice", 4.0),
            ("Chicken Wings", 7.0),
            ("Ice Cream", 4.5)
        ]
        self.revenue = 0.0
        self.rev_lock = threading.Lock()
    
    def purchase(self, client_id):
        """Simulate a client buying a random snack or drink."""
        item, price = random.choice(self.items)
        with self.rev_lock:
            self.revenue += price
        print(f"Client {client_id} bought {item} for ${price:.2f}")

# Bowling alley simulation class
class BowlingAlley:
    def __init__(self, num_lanes=10):
        self.num_lanes = num_lanes
        self.free_lanes = list(range(1, num_lanes + 1))    # IDs of free lanes
        self.queue = []                                    # waiting clients (Client objects)
        self.lock = threading.Lock()                       
        self.condition = threading.Condition(self.lock)    # condition for lane availability
    
    def request_lane(self, client):
        """Client requests to use a lane. Will wait if necessary until assigned to a lane."""
        with self.lock:
            # Client enters the waiting queue
            self.queue.append(client)
            client.assigned = False
            # Wait until this client is first in queue and a lane is free (or until assigned to a group)
            while True:
                # If this client has been assigned to a group by another thread, stop waiting
                if client.assigned:
                    break
                # If a lane is free and this client is at front of the queue, assign a group to a lane
                if self.free_lanes and self.queue[0] is client:
                    # Allocate the first available lane
                    lane_id = self.free_lanes.pop(0)
                    # Form a group of up to 4 clients from the queue (including this client)
                    group = []
                    group_size = min(4, len(self.queue))
                    for i in range(group_size):
                        member = self.queue.pop(0)
                        member.assigned = True   # mark each group member as assigned to a lane
                        group.append(member)
                    # Use one shared Event for the group to signal when their session is finished
                    session_done = threading.Event()
                    for member in group:
                        member.finished_event = session_done
                    print(f"Group of {len(group)} (clients {[m.id for m in group]}) is starting to bowl on lane {lane_id}")
                    # Start a separate thread to simulate the bowling session for this group
                    threading.Thread(target=self._bowl_session, args=(lane_id, group, session_done)).start()
                    break
                # Otherwise, wait until a lane becomes free or this client gets assigned
                self.condition.wait()
        # Lock is released here. If the client was part of a group, wait for that bowling session to finish.
        if hasattr(client, 'finished_event'): #Does this client object have an attribute named finished_event?
            client.finished_event.wait()
        # At this point, the bowling session is done and the client can proceed (or exit).
    
    def _bowl_session(self, lane_id, group, session_done_event):
        """Simulate a bowling session for a group on a given lane, freeing the lane afterward."""
        # Simulate the time taken for a bowling session (2 to 3 seconds)
        time.sleep(random.uniform(2.0, 3.0))
        print(f"Group (clients {[m.id for m in group]}) finished bowling on lane {lane_id}")
        # Mark the lane as free and notify waiting clients
        with self.lock:
            self.free_lanes.append(lane_id)
            self.free_lanes.sort()
            # Notify all waiting clients that a lane has become free
            self.condition.notify_all()
        # Signal all group members that their session is complete
        session_done_event.set()

# Client class representing a person arriving to bowl
class Client:
    def __init__(self, client_id, alley, snack_bar):
        self.id = client_id
        self.alley = alley
        self.snack_bar = snack_bar
        self.assigned = False
        self.finished_event = None
    
    def go_bowling(self):
        """Simulate the client’s bowling visit, including optional snack purchases."""
        # Randomly decide if the client buys a snack and whether it's before or after bowling
        purchase_timing = random.choice(["none", "before", "after"])
        if purchase_timing == "before":
            # Buy a snack before bowling
            self.snack_bar.purchase(self.id)
       
        # Request a lane (this may block until a lane/group is available)
        self.alley.request_lane(self) # <-- ALWAYS runs (outside the ifs)
        
        if purchase_timing == "after":
            # Buy a snack after finishing bowling
            self.snack_bar.purchase(self.id)

# --- Simulation Execution (if run as a script) ---
if __name__ == "__main__":
    # Initialize the bowling alley and snack bar
    alley = BowlingAlley(num_lanes=10)
    snack_bar = SnackBar()
    # Create a number of clients to simulate (arriving as separate threads)
    clients = [Client(i, alley, snack_bar) for i in range(1, 41)]  # e.g., 40 clients
    threads = []
    # Start client threads (simulating random arrival times)
    for client in clients:
        # Introduce a small random delay to mimic random arrivals
        time.sleep(random.uniform(0.1, 0.5))
        t = threading.Thread(target=client.go_bowling)
        threads.append(t)
        t.start()
    # Wait for all clients to finish
    for t in threads:
        t.join()
    # Print total snack bar revenue at the end
    print(f"Total snack bar revenue: ${snack_bar.revenue:.2f}")
