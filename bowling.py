import threading
import time
import random

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
    
    def purchase(self, client):
        """Simulate a client buying a random snack or drink."""
        item, price = random.choice(self.items)
        with self.rev_lock:
            self.revenue += price
        print(f"Client {client.id} bought {item} for ${price:.2f}")
        client.log_activity(
            amenity="Bowling snack bar",
            action="Purchase",
            success=True,
            info=f"Item: {item}, Price: {price:.2f}"
        )

class BowlingAlley:
    def __init__(self, num_lanes=10):
        self.num_lanes = num_lanes
        self.free_lanes = list(range(1, num_lanes + 1))    # IDs of free lanes
        self.queue = []                                    # waiting clients
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)

    def request_lane(self, client):
        """Client requests to use a lane. Will wait if necessary until assigned to a lane."""
        with self.lock:
            # Client enters the waiting queue
            self.queue.append(client)
            client.assigned = False
            client.log_activity(
                amenity="Bowling lane",
                action="Join queue",
                success=True,
                info="Waiting for lane"
            )

            while True:
                # If this client has been assigned, stop waiting
                if client.assigned:
                    break

                # If a lane is free and this client is first in queue, form a group
                if self.free_lanes and self.queue[0] is client:
                    lane_id = self.free_lanes.pop(0)

                    group = []
                    group_size = min(4, len(self.queue))
                    for i in range(group_size):
                        member = self.queue.pop(0)
                        member.assigned = True
                        group.append(member)

                    session_done = threading.Event()
                    for member in group:
                        member.finished_event = session_done
                        member.log_activity(
                            amenity="Bowling lane",
                            action="Start session",
                            success=True,
                            info=f"Lane {lane_id} with group {[m.id for m in group]}"
                        )

                    print(f"Group of {len(group)} (clients {[m.id for m in group]}) is starting to bowl on lane {lane_id}")

                    threading.Thread(
                        target=self._bowl_session,
                        args=(lane_id, group, session_done)
                    ).start()
                    break

                # Otherwise wait
                self.condition.wait()

        # After assigned, wait until the group session is done
        if hasattr(client, 'finished_event'):
            client.finished_event.wait()

    def _bowl_session(self, lane_id, group, session_done_event):
        """Simulate a bowling session for a group on a given lane."""
        time.sleep(random.uniform(2.0, 3.0))
        print(f"Group (clients {[m.id for m in group]}) finished bowling on lane {lane_id}")
        for member in group:
            member.log_activity(
                amenity="Bowling lane",
                action="End session",
                success=True,
                info=f"Lane {lane_id}"
            )

        with self.lock:
            self.free_lanes.append(lane_id)
            self.free_lanes.sort()
            # Notify all waiting clients that a lane has become free
            self.condition.notify_all()

        # Signal all group members that their session is complete
        session_done_event.set()

class Client:
    """
    Local Client used in this file for now.
    In the integrated project, this should be replaced
    by the global Client class that already defines log_activity.
    """
    def __init__(self, client_id, alley, snack_bar):
        self.id = client_id
        self.alley = alley
        self.snack_bar = snack_bar
        self.assigned = False
        self.finished_event = None
    
    def log_activity(self, amenity, action, success, info=""):
        print(f"[LOG] Client {self.id} | {amenity} | {action} | success={success} | {info}")

    def go_bowling(self):
        """Simulate the client’s bowling visit, including optional snack purchases."""
        purchase_timing = random.choice(["none", "before", "after"])

        if purchase_timing == "before":
            self.snack_bar.purchase(self)

        self.alley.request_lane(self)

        if purchase_timing == "after":
            self.snack_bar.purchase(self)

def main():
    alley = BowlingAlley(num_lanes=10)
    snack_bar = SnackBar()

    clients = [Client(i, alley, snack_bar) for i in range(1, 41)]
    threads = []

    for client in clients:
        time.sleep(random.uniform(0.1, 0.5))
        t = threading.Thread(target=client.go_bowling)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print(f"Total snack bar revenue: ${snack_bar.revenue:.2f}")

if __name__ == "__main__":
    main()

