import threading
import time
import random
from collections import deque


class StaffMember:
    def _init_(self, staff_id, name, skills):
        """
        skills: list of area names or task types the staff member is good at.
        e.g. ["Locker Rooms", "Lobby", "Restaurant"]
        """
        self.staff_id = staff_id
        self.name = name
        self.skills = set(skills)
        self.completed_tasks = 0

    def _str_(self):
        return f"{self.name} (ID: {self.staff_id})"


class Area:
    def _init_(self, area_id, name, priority=1):
        self.area_id = area_id
        self.name = name
        self.priority = priority  # could be used to prioritize tasks

    def _str_(self):
        return f"{self.name}"


class CleaningTask:
    def _init_(self, task_id, area, description, scheduled_time, estimated_duration):
        """
        area: Area object
        scheduled_time: when task is planned to start (timestamp)
        estimated_duration: simulated 'minutes' or seconds in our simulation
        """
        self.task_id = task_id
        self.area = area
        self.description = description
        self.scheduled_time = scheduled_time
        self.estimated_duration = estimated_duration

        self.assigned_to = None  # StaffMember
        self.status = "PENDING"  # PENDING, IN_PROGRESS, COMPLETED

    def _str_(self):
        assigned_name = self.assigned_to.name if self.assigned_to else "Unassigned"
        return (f"Task {self.task_id} - {self.description} in {self.area.name} "
                f"[{self.status}] (Assigned to: {assigned_name})")


class CleaningManager:
    def _init_(self):
        self.lock = threading.RLock()

        self.areas = []
        self.staff_members = []

        # Task lists
        self.pending_tasks = deque()
        self.tasks_in_progress = {}
        self.completed_tasks = []

        self.task_counter = 1

        print("Cleaning Manager initialized.\n")

    # ----- Area & Staff registration -----

    def add_area(self, area):
        with self.lock:
            self.areas.append(area)
            print(f"Registered Area: {area.name}")

    def add_staff_member(self, staff_member):
        with self.lock:
            self.staff_members.append(staff_member)
            print(f"Registered Staff Member: {staff_member}")

    # ----- Task creation & management -----

    def create_task(self, area, description, estimated_duration):
        """
        Creates a new task and adds it to the pending queue.
        """
        with self.lock:
            task_id = self.task_counter
            self.task_counter += 1

            scheduled_time = time.time()
            task = CleaningTask(task_id, area, description, scheduled_time, estimated_duration)
            self.pending_tasks.append(task)

            print(f"New CleaningTask created: {task}")
            print(f"Pending tasks: {len(self.pending_tasks)}\n")

            return task

    def _find_suitable_task_for_staff(self, staff_member):
        """
        Helper: find the first pending task that matches staff skills (by area name).
        If none match, return None.
        """
        for idx, task in enumerate(self.pending_tasks):
            if task.area.name in staff_member.skills or not staff_member.skills:
                return idx, task
        return None, None

    def assign_task_to_staff(self, staff_member):
        """
        Called by staff worker threads to get a task.
        """
        with self.lock:
            if not self.pending_tasks:
                return None

            idx, task = self._find_suitable_task_for_staff(staff_member)
            if task is None:
                # no suitable task for this staff member
                return None

            # Remove task from pending queue by index
            del self.pending_tasks[idx]

            task.assigned_to = staff_member
            task.status = "IN_PROGRESS"
            self.tasks_in_progress[task.task_id] = task

            print(f"Task {task.task_id} ASSIGNED to {staff_member.name}")
            print(f" -> {task.description} in {task.area.name}")
            print(f"Pending tasks: {len(self.pending_tasks)}, In-progress: {len(self.tasks_in_progress)}\n")

            return task

    def mark_task_complete(self, task, staff_member):
        """
        Called when a staff member finishes a task.
        """
        with self.lock:
            if task.task_id in self.tasks_in_progress:
                del self.tasks_in_progress[task.task_id]

            task.status = "COMPLETED"
            self.completed_tasks.append(task)
            staff_member.completed_tasks += 1

            print(f"Task {task.task_id} COMPLETED by {staff_member.name}")
            print(f" -> {task.description} in {task.area.name}")
            print(f"Completed tasks: {len(self.completed_tasks)}\n")

    def get_status_snapshot(self):
        with self.lock:
            return {
                "pending_tasks": len(self.pending_tasks),
                "in_progress_tasks": len(self.tasks_in_progress),
                "completed_tasks": len(self.completed_tasks),
            }


# ----- STAFF THREAD FUNCTION -----

def staff_worker_thread(staff_member, manager, simulation_duration=60):
    """
    Each staff member runs in its own thread:
    - asks for tasks
    - executes them (simulated by sleep)
    - marks them complete
    """
    print(f"[STAFF THREAD STARTED] {staff_member.name} is now on shift.\n")
    start_time = time.time()

    while time.time() - start_time < simulation_duration:
        task = manager.assign_task_to_staff(staff_member)

        if task:
            # Simulate doing the cleaning work
            # estimated_duration is in "seconds" for this simulation
            work_time = task.estimated_duration
            print(f"{staff_member.name} is working on Task {task.task_id} "
                  f"in {task.area.name} for ~{work_time:.1f} seconds.")
            time.sleep(work_time)

            manager.mark_task_complete(task, staff_member)
        else:
            # No task right now, small break / idle
            print(f"{staff_member.name} has no task right now. Waiting...\n")
            time.sleep(random.uniform(2, 5))

    print(f"[STAFF THREAD ENDED] {staff_member.name}'s shift is over.\n")


# ----- TASK GENERATOR FUNCTION (SCHEDULE) -----

def task_generator_cleaning(manager, simulation_duration=60):
    """
    Simulates the creation of cleaning tasks over time.
    Acts as the "schedule" that says:
      - At 8:00 clean locker rooms
      - At 9:00 clean lobby
      - After tournament clean restaurant
    In this simulation, we randomly create tasks for different areas.
    """
    print("[SCHEDULE] Cleaning task generator started.\n")

    descriptions = [
        "Sweep and mop the floor",
        "Disinfect all surfaces",
        "Restock towels and supplies",
        "Empty trash bins",
        "Clean mirrors and windows",
        "Deep clean after event",
    ]

    start_time = time.time()
    while time.time() - start_time < simulation_duration:
        # Every few seconds a new task appears
        time.sleep(random.randint(3, 7))

        with manager.lock:
            if not manager.areas:
                continue
            area = random.choice(manager.areas)

        description = random.choice(descriptions)
        # estimated_duration between 5 and 12 seconds to simulate work
        estimated_duration = random.uniform(5, 12)

        manager.create_task(area, description, estimated_duration)

    print("[SCHEDULE] Cleaning task generator finished.\n")


# ----- MAIN SIMULATION -----

def main():
    print("CLEANING STAFF SIMULATION (Country Club)\n")

    manager = CleaningManager()

    # Define areas that must stay clean
    locker_rooms = Area(1, "Locker Rooms", priority=2)
    lobby = Area(2, "Lobby", priority=1)
    restaurant = Area(3, "Restaurant", priority=3)
    courtside = Area(4, "Courtside", priority=2)

    manager.add_area(locker_rooms)
    manager.add_area(lobby)
    manager.add_area(restaurant)
    manager.add_area(courtside)

    print()

    # Register cleaning staff members and their skills
    alice = StaffMember(1, "Alice", ["Locker Rooms", "Lobby"])
    bob = StaffMember(2, "Bob", ["Restaurant", "Lobby"])
    carol = StaffMember(3, "Carol", ["Courtside", "Locker Rooms", "Restaurant"])

    manager.add_staff_member(alice)
    manager.add_staff_member(bob)
    manager.add_staff_member(carol)

    print("\n--- Starting Cleaning Simulation ---\n")

    # Total simulation duration (seconds)
    simulation_duration = 60

    # Start task generator thread (schedule)
    schedule_thread = threading.Thread(
        target=task_generator_cleaning,
        args=(manager, simulation_duration),
        daemon=True
    )
    schedule_thread.start()

    # Start staff threads (each staff member is a thread)
    staff_threads = []
    for staff in manager.staff_members:
        t = threading.Thread(
            target=staff_worker_thread,
            args=(staff, manager, simulation_duration + 10),  # staff stays a bit longer
            daemon=True
        )
        t.start()
        staff_threads.append(t)

    # Wait for staff threads to end (main thread will wait)
    for t in staff_threads:
        t.join()

    # Final status
    snapshot = manager.get_status_snapshot()
    print("\n--- SIMULATION ENDED ---")
    print("Final Cleaning Manager Status:")
    print(f"  Pending tasks:    {snapshot['pending_tasks']}")
    print(f"  In-progress tasks:{snapshot['in_progress_tasks']}")
    print(f"  Completed tasks:  {snapshot['completed_tasks']}\n")

    print("Tasks completed per staff:")
    for staff in manager.staff_members:
        print(f"  {staff.name}: {staff.completed_tasks} tasks completed")


if _name_ == "_main_":
    main()