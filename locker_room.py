import threading
import time
import random
from collections import deque


class LockerRoomArea:
    def __init__(self, gender_label, total_lockers=10, total_showers=4):
        self.gender_label = gender_label
        self.total_lockers = total_lockers
        self.total_showers = total_showers
        self.available_lockers = total_lockers
        self.available_showers = total_showers
        self.lock = threading.RLock()
        self.shower_condition = threading.Condition(self.lock)
        self.waiting_clients = deque()

        print(f"{self.gender_label} Locker Room initialized with "
              f"{self.total_lockers} lockers and {self.total_showers} showers.")

    def use_locker_room(self, client, gender, wants_shower=True):
        with self.lock:
            print(f"Client {client.id} ({gender}) arrived to {self.gender_label} Locker Room "
                  f"({'wants shower' if wants_shower else 'no shower'})")

            if self.available_lockers > 0:
                self._start_locker_session(client, gender, wants_shower)
            else:
                self.waiting_clients.append((client, gender, wants_shower))
                print(f"Client {client.id} waits for a locker in {self.gender_label} room. "
                      f"Waiting clients: {len(self.waiting_clients)}")

                client.log_activity(
                    amenity=f"{self.gender_label} Locker Room",
                    action="Join locker queue",
                    success=True,
                    info=f"Queue position: {len(self.waiting_clients)}"
                )

    def _start_locker_session(self, client, gender, wants_shower):
        self.available_lockers -= 1
        locker_number = self.total_lockers - self.available_lockers

        print(f"Locker session STARTED for Client {client.id} "
              f"at {self.gender_label} Locker {locker_number}")

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
        change_time_before = random.uniform(3, 7)
        print(f"Client {client.id} is changing at {self.gender_label} Locker {locker_number} "
              f"(~{change_time_before:.1f}s)")
        time.sleep(change_time_before)

        client.log_activity(
            amenity=f"{self.gender_label} Locker Room",
            action="Changed before activity",
            success=True,
            info=f"Locker {locker_number}, Duration: {change_time_before:.1f}s"
        )

        if wants_shower:
            self._use_shower(client, gender, locker_number)

        change_time_after = random.uniform(2, 5)
        print(f"Client {client.id} is changing after activity at "
              f"{self.gender_label} Locker {locker_number} (~{change_time_after:.1f}s)")
        time.sleep(change_time_after)

        client.log_activity(
            amenity=f"{self.gender_label} Locker Room",
            action="Changed after activity",
            success=True,
            info=f"Locker {locker_number}, Duration: {change_time_after:.1f}s"
        )

        with self.lock:
            self.available_lockers += 1
            print(f"Client {client.id} LEFT {self.gender_label} Locker {locker_number}")

            client.log_activity(
                amenity=f"{self.gender_label} Locker Room",
                action="Locker session completed",
                success=True,
                info=f"Locker {locker_number}, Total time: {change_time_before + change_time_after + (8 if wants_shower else 0):.1f}s"
            )

            if self.waiting_clients:
                next_client, next_gender, next_wants_shower = self.waiting_clients.popleft()
                print(f"Assigning freed {self.gender_label} locker to waiting Client {next_client.id}")
                self._start_locker_session(next_client, next_gender, next_wants_shower)

    def _use_shower(self, client, gender, locker_number):
        with self.lock:
            while self.available_showers == 0:
                print(f"Client {client.id} wants a shower in {self.gender_label} room "
                      f"but none are available. Waiting...")

                client.log_activity(
                    amenity=f"{self.gender_label} Locker Room",
                    action="Wait for shower",
                    success=True,
                    info=f"Locker {locker_number}"
                )

                self.shower_condition.wait()

            self.available_showers -= 1
            shower_number = self.total_showers - self.available_showers
            print(f"Client {client.id} ENTERED {self.gender_label} Shower {shower_number}")

        shower_time = random.uniform(4, 8)
        time.sleep(shower_time)

        client.log_activity(
            amenity=f"{self.gender_label} Locker Room",
            action="Used shower",
            success=True,
            info=f"Shower {shower_number}, Duration: {shower_time:.1f}s"
        )

        with self.lock:
            self.available_showers += 1
            print(f"Client {client.id} LEFT {self.gender_label} Shower {shower_number}")
            self.shower_condition.notify()



