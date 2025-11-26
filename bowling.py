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

    def purchase(self, client):
        """Simulate a client buying a random snack or drink."""
        item, price = random.choice(self.items)
        with self.rev_lock:
            self.revenue += price

        print(f"Client {client.id} bought {item} for ${price:.2f}")

        # ✅ LOG: Snack purchase
        client.log_activity(
            amenity="Bowling Snack Bar",
            action="Purchase snack",
            success=True,
            info=f"{item} for ${price:.2f}"
        )


# Bowling alley simulation class
class BowlingAlley:
    def __init__(self, num_lanes=10):
        self.num_lanes = num_lanes
        self.free_lanes = list(range(1, num_lanes + 1))  # IDs of free lanes
        self.queue = []  # waiting clients (Client objects)
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)  # condition for lane availability

    def request_lane(self, client):
        """Client requests to use a lane. Will wait if necessary until assigned to a lane."""
        with self.lock:
            # Client enters the waiting queue
            self.queue.append(client)
            client.assigned = False

            # ✅ LOG: Joined bowling queue
            client.log_activity(
                amenity="Bowling Alley",
                action="Join queue",
                success=True,
                info=f"Queue position: {len(self.queue)}"
            )

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
                        member.assigned = True  # mark each group member as assigned to a lane
                        group.append(member)
                    # Use one shared Event for the group to signal when their session is finished
                    session_done = threading.Event()
                    for member in group:
                        member.finished_event = session_done

                    print(
                        f"Group of {len(group)} (clients {[m.id for m in group]}) is starting to bowl on lane {lane_id}")

                    # ✅ LOG: Lane assigned and group formed
                    for member in group:
                        member.log_activity(
                            amenity="Bowling Alley",
                            action="Lane assigned",
                            success=True,
                            info=f"Lane {lane_id}, Group: {[m.id for m in group]}"
                        )

                    # Start a separate thread to simulate the bowling session for this group
                    threading.Thread(target=self._bowl_session, args=(lane_id, group, session_done)).start()
                    break
                # Otherwise, wait until a lane becomes free or this client gets assigned
                self.condition.wait()

        # Lock is released here. If the client was part of a group, wait for that bowling session to finish.
        if hasattr(client, 'finished_event'):
            client.finished_event.wait()

        # At this point, the bowling session is done and the client can proceed (or exit).

    def _bowl_session(self, lane_id, group, session_done_event):
        """Simulate a bowling session for a group on a given lane, freeing the lane afterward."""
        # Simulate the time taken for a bowling session (2 to 3 seconds)
        session_duration = random.uniform(2.0, 3.0)
        time.sleep(session_duration)

        print(f"Group (clients {[m.id for m in group]}) finished bowling on lane {lane_id}")

        # ✅ LOG: Bowling session completed for all group members
        for member in group:
            member.log_activity(
                amenity="Bowling Alley",
                action="Finish bowling",
                success=True,
                info=f"Lane {lane_id}, Duration: {session_duration:.1f}s, Group: {[m.id for m in group]}"
            )

        # Mark the lane as free and notify waiting clients
        with self.lock:
            self.free_lanes.append(lane_id)
            self.free_lanes.sort()
            # Notify all waiting clients that a lane has become free
            self.condition.notify_all()

        # Signal all group members that their session is complete
        session_done_event.set()

# REMOVED: Local Client class - using controller's Client instead
# REMOVED: go_bowling method - integrated into controller
# REMOVED: Standalone simulation code