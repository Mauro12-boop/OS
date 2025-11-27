
import threading
import time
import random
from collections import deque


class LockerRoomArea:
    def __init__(self, gender_label, total_lockers=10, total_showers=4):
        self.gender_label = gender_label  # "Male" or "Female"

        self.total_lockers = total_lockers
        self.total_showers = total_showers

        self.available_lockers = total_lockers
        self.available_showers = total_showers

        # Main re-entrant lock to protect shared state
        self.lock = threading.RLock()

        # Condition for waiting on showers
        self.shower_condition = threading.Condition(self.lock)

        # Queue of clients waiting to get a locker (resource)
        self.waiting_clients = deque()

        print(f"{self.gender_label} Locker Room initialized with "
              f"{self.total_lockers} lockers and {self.total_showers} showers.")

    # ------------- Public API for client integration -------------

    def use_locker_room(self, client, gender, wants_shower=True):
        """
        Main method for clients to use the locker room
        """
        with self.lock:
            print(f"Client {client.id} ({gender}) arrived to {self.gender_label} Locker Room "
                  f"({'wants shower' if wants_shower else 'no shower'})")

            if self.available_lockers > 0:
                # Assign a locker immediately and start their session
                self._start_locker_session(client, gender, wants_shower)
            else:
                # No locker available → wait in queue
                self.waiting_clients.append((client, gender, wants_shower))
                print(f"Client {client.id} waits for a locker in {self.gender_label} room. "
                      f"Waiting clients: {len(self.waiting_clients)}")
                
                # ✅ LOG: Joined locker queue
                client.log_activity(
                    amenity=f"{self.gender_label} Locker Room",
                    action="Join locker queue",
                    success=True,
                    info=f"Queue position: {len(self.waiting_clients)}"
                )

    # ------------- Internal logic -------------

    def _start_locker_session(self, client, gender, wants_shower):
        """
        Reserve a locker and start a new thread to simulate the client's
        locker room usage (changing, showering, leaving).
        """
        self.available_lockers -= 1
        locker_number = self.total_lockers - self.available_lockers

        print(f"Locker session STARTED for Client {client.id} "
              f"at {self.gender_label} Locker {locker_number}")
        
        # ✅ LOG: Locker assigned
        client.log_activity(
            amenity=f"{self.gender_label} Locker Room",
            action="Locker assigned",
            success=True,
            info=f"Locker {locker_number}"
        )

        threading.Thread(
            target=self._run_locker_session,
            args=(client, gender, wants_shower, locker_number),
            daemon=True
        ).start()

    def _run_locker_session(self, client, gender, wants_shower, locker_number):
        """
        Simulate the full lifecycle of a client using the locker room:
        - Changing before activity
        - Possibly using a shower
        - Changing again / leaving
        """
        # Simulate changing before activity
        change_time_before = random.uniform(3, 7)
        print(f"Client {client.id} is changing at {self.gender_label} Locker {locker_number} "
              f"(~{change_time_before:.1f}s)")
        time.sleep(change_time_before)

        # ✅ LOG: Changed before activity
        client.log_activity(
            amenity=f"{self.gender_label} Locker Room",
            action="Changed before activity",
            success=True,
            info=f"Locker {locker_number}, Duration: {change_time_before:.1f}s"
        )

        # Optional shower usage
        if wants_shower:
            self._use_shower(client, gender, locker_number)

        # Simulate changing again after shower/activity
        change_time_after = random.uniform(2, 5)
        print(f"Client {client.id} is changing after activity at "
              f"{self.gender_label} Locker {locker_number} (~{change_time_after:.1f}s)")
        time.sleep(change_time_after)

        # ✅ LOG: Changed after activity
        client.log_activity(
            amenity=f"{self.gender_label} Locker Room",
            action="Changed after activity",
            success=True,
            info=f"Locker {locker_number}, Duration: {change_time_after:.1f}s"
        )

        # Client leaves, free the locker and potentially assign it to someone waiting
        with self.lock:
            self.available_lockers += 1
            print(f"Client {client.id} LEFT {self.gender_label} Locker {locker_number}")
            
            # ✅ LOG: Locker session completed
            client.log_activity(
                amenity=f"{self.gender_label} Locker Room",
                action="Locker session completed",
                success=True,
                info=f"Locker {locker_number}, Total time: {change_time_before + change_time_after + (8 if wants_shower else 0):.1f}s"
            )

            # If someone is waiting for a locker, start their session
            if self.waiting_clients:
                next_client, next_gender, next_wants_shower = self.waiting_clients.popleft()
                print(f"Assigning freed {self.gender_label} locker to waiting Client {next_client.id}")
                self._start_locker_session(next_client, next_gender, next_wants_shower)

    def _use_shower(self, client, gender, locker_number):
        """
        Simulate a client using a shower:
        - Waits if no shower is available using a Condition
        - Uses shower for a random time
        - Frees shower and notifies others waiting
        """
        with self.lock:
            while self.available_showers == 0:
                print(f"Client {client.id} wants a shower in {self.gender_label} room "
                      f"but none are available. Waiting...")
                
                # ✅ LOG: Waiting for shower
                client.log_activity(
                    amenity=f"{self.gender_label} Locker Room",
                    action="Wait for shower",
                    success=True,
                    info=f"Locker {locker_number}"
                )
                
                self.shower_condition.wait()

            # Reserve a shower
            self.available_showers -= 1
            shower_number = self.total_showers - self.available_showers
            print(f"Client {client.id} ENTERED {self.gender_label} Shower {shower_number}")

        # Simulate shower time outside the lock
        shower_time = random.uniform(4, 8)
        time.sleep(shower_time)

        # ✅ LOG: Shower used
        client.log_activity(
            amenity=f"{self.gender_label} Locker Room",
            action="Used shower",
            success=True,
            info=f"Shower {shower_number}, Duration: {shower_time:.1f}s"
        )

        # Free shower and notify one waiting client (if any)
        with self.lock:
            self.available_showers += 1
            print(f"Client {client.id} LEFT {self.gender_label} Shower {shower_number}")
            self.shower_condition.notify()

    def get_status(self):
        """
        Snapshot of current locker room status.
        """
        with self.lock:
            return {
                "available_lockers": self.available_lockers,
                "available_showers": self.available_showers,
                "waiting_clients": len(self.waiting_clients),
            }

# REMOVED: member_arrivals_lockerrooms function - integrated into controller
# REMOVED: main function - integrated into controller
# REMOVED: Local simulation code