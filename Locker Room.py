
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

        # Queue of members waiting to get a locker (resource)
        # Each entry: (member_id, wants_shower, gender)
        self.waiting_members = deque()

        print(f"{self.gender_label} Locker Room initialized with "
              f"{self.total_lockers} lockers and {self.total_showers} showers.")
        print(f"Available lockers: {self.available_lockers}")
        print(f"Available showers: {self.available_showers}\n")

    # ------------- Public API for arrivals -------------

    def handle_member_arrival(self, member_id, gender, wants_shower=True):
        """
        Called whenever a club member arrives at this specific locker room.
        Each member wants a locker and may or may not plan to use a shower.
        """
        with self.lock:
            print(f"{gender} Member_{member_id} arrived to {self.gender_label} Locker Room "
                  f"({'wants shower' if wants_shower else 'no shower'})")

            if self.available_lockers > 0:
                # Assign a locker immediately and start their session
                self._start_locker_session(member_id, gender, wants_shower)
            else:
                # No locker available → wait in queue
                self.waiting_members.append((member_id, gender, wants_shower))
                print(f" {gender} Member_{member_id} waits for a locker in {self.gender_label} room. "
                      f"Waiting members: {len(self.waiting_members)}\n")

    # ------------- Internal logic -------------

    def _start_locker_session(self, member_id, gender, wants_shower):
        """
        Reserve a locker and start a new thread to simulate the member's
        locker room usage (changing, showering, leaving).
        """
        self.available_lockers -= 1
        locker_number = self.total_lockers - self.available_lockers

        print(f"Locker session STARTED for {gender} Member_{member_id} "
              f"at {self.gender_label} Locker {locker_number}")
        print(f"{self.gender_label} available lockers: "
              f"{self.available_lockers}/{self.total_lockers}\n")

        threading.Thread(
            target=self._run_locker_session,
            args=(member_id, gender, wants_shower, locker_number),
            daemon=True
        ).start()

    def _run_locker_session(self, member_id, gender, wants_shower, locker_number):
        """
        Simulate the full lifecycle of a member using the locker room:
        - Changing before activity
        - Possibly using a shower
        - Changing again / leaving
        """
        # Simulate changing before activity
        change_time_before = random.uniform(3, 7)
        print(f" {gender} Member_{member_id} is changing at {self.gender_label} Locker {locker_number} "
              f"(~{change_time_before:.1f}s)")
        time.sleep(change_time_before)

        # Optional shower usage
        if wants_shower:
            self._use_shower(member_id, gender)

        # Simulate changing again after shower/activity
        change_time_after = random.uniform(2, 5)
        print(f" {gender} Member_{member_id} is changing after activity at "
              f"{self.gender_label} Locker {locker_number} (~{change_time_after:.1f}s)")
        time.sleep(change_time_after)

        # Member leaves, free the locker and potentially assign it to someone waiting
        with self.lock:
            self.available_lockers += 1
            print(f" {gender} Member_{member_id} LEFT {self.gender_label} Locker {locker_number}")
            print(f" Now available lockers in {self.gender_label}: "
                  f"{self.available_lockers}/{self.total_lockers}")

            # If someone is waiting for a locker, start their session
            if self.waiting_members:
                next_member_id, next_gender, next_wants_shower = self.waiting_members.popleft()
                print(f" Assigning freed {self.gender_label} locker to waiting "
                      f"{next_gender} Member_{next_member_id}")
                self._start_locker_session(next_member_id, next_gender, next_wants_shower)
            print()  # blank line for readability

    def _use_shower(self, member_id, gender):
        """
        Simulate a member using a shower:
        - Waits if no shower is available using a Condition
        - Uses shower for a random time
        - Frees shower and notifies others waiting
        """
        with self.lock:
            while self.available_showers == 0:
                print(f" {gender} Member_{member_id} wants a shower in {self.gender_label} room "
                      f"but none are available. Waiting...")
                self.shower_condition.wait()

            # Reserve a shower
            self.available_showers -= 1
            shower_number = self.total_showers - self.available_showers
            print(f" {gender} Member_{member_id} ENTERED {self.gender_label} Shower {shower_number}")
            print(f" Available showers in {self.gender_label}: "
                  f"{self.available_showers}/{self.total_showers}\n")

        # Simulate shower time outside the lock
        shower_time = random.uniform(4, 8)
        time.sleep(shower_time)

        # Free shower and notify one waiting member (if any)
        with self.lock:
            self.available_showers += 1
            print(f" {gender} Member_{member_id} LEFT {self.gender_label} Shower {shower_number}")
            print(f" Now available showers in {self.gender_label}: "
                  f"{self.available_showers}/{self.total_showers}")
            self.shower_condition.notify()
            print()

    def get_status(self):
        """
        Snapshot of current locker room status.
        """
        with self.lock:
            return {
                "available_lockers": self.available_lockers,
                "available_showers": self.available_showers,
                "waiting_members": len(self.waiting_members),
            }


# ------------- Arrival Simulation (both genders) -------------

def member_arrivals_lockerrooms(male_locker_room, female_locker_room, simulation_duration=60):
    """
    Simulate club members (both genders) arriving at the locker rooms over time.
    Each member is randomly assigned Male/Female and routed to the corresponding room.
    """
    member_counter = 1
    start_time = time.time()

    print("LOCKER ROOMS are OPEN for members!\n")

    genders = ["Male", "Female"]

    while time.time() - start_time < simulation_duration:
        # Random delay between arrivals
        time.sleep(random.randint(1, 5))

        gender = random.choice(genders)
        wants_shower = random.random() < 0.7  # 70% chance of wanting a shower

        if gender == "Male":
            male_locker_room.handle_member_arrival(member_counter, gender, wants_shower=wants_shower)
        else:
            female_locker_room.handle_member_arrival(member_counter, gender, wants_shower=wants_shower)

        member_counter += 1

    print("\nLOCKER ROOMS are now CLOSED for new arrivals!")

    # Final status snapshots
    male_status = male_locker_room.get_status()
    female_status = female_locker_room.get_status()

    print("\nEnd-of-day Locker Room Summary:")
    print(" Male Locker Room:")
    print(f"   Available lockers: {male_status['available_lockers']}/{male_locker_room.total_lockers}")
    print(f"   Available showers: {male_status['available_showers']}/{male_locker_room.total_showers}")
    print(f"   Members still waiting for locker: {male_status['waiting_members']}")
    print()
    print(" Female Locker Room:")
    print(f"   Available lockers: {female_status['available_lockers']}/{female_locker_room.total_lockers}")
    print(f"   Available showers: {female_status['available_showers']}/{female_locker_room.total_showers}")
    print(f"   Members still waiting for locker: {female_status['waiting_members']}")


# ------------- Main -------------

def main():
    print("GENDER-SEPARATED LOCKER ROOM USAGE SIMULATION (Country Club)\n")

    # Create two locker room areas: Male and Female
    male_locker_room = LockerRoomArea("Male", total_lockers=8, total_showers=3)
    female_locker_room = LockerRoomArea("Female", total_lockers=8, total_showers=3)

    # Run the arrival simulation for N seconds
    member_arrivals_lockerrooms(male_locker_room, female_locker_room, simulation_duration=80)

    # Give some extra time for ongoing sessions (daemon threads) to finish
    print("\nWaiting a bit for ongoing locker/shower sessions to complete...")
    time.sleep(20)
    print("Simulation finished.")


if __name__ == "__main__":
    main()