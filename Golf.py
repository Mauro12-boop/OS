import random
import threading
import time

class GolfCourse:
    def __init__(self):
        self.holes = None
        self.carts = None
        self.range_slots = None
        self.range_lock = threading.RLock()
        self.course_lock = threading.RLock()

    def practice_range(self, client):
        # Client tries to practice at the driving range
        with self.range_lock:
            slot = None
            for s in self.range_slots:
                if not s.is_occupied:
                    slot = s
                    break
        if slot:
            # Log + start practice session
            client.log_activity(
                amenity="Golf driving range",
                action="Start practice",
                success=True,
                info=f"Slot {slot.id}"
            )
            slot.practice_session(client, slot.id)
        else:
            print(f"client {client.id} could not practice at the driving range - all slots were full")
            client.log_activity(
                amenity="Golf driving range",
                action="Start practice",
                success=False,
                info="All slots were full"
            )

    def play_course(self, client):
        # Client tries to start a golf round on the course
        with self.course_lock:
            hole = None
            cart = None

            # Find an available hole
            for h in self.holes:
                if not h.is_occupied:
                    h.is_occupied = True
                    h.client = client
                    hole = h
                    break

            # Find an available cart
            for c in self.carts:
                if c.is_available:
                    c.is_available = False
                    c.assigned_client = client
                    cart = c
                    break

            # If either hole or cart is not available, roll back and exit
            if hole is None or cart is None:
                if hole is not None:
                    hole.is_occupied = False
                    hole.client = None
                if cart is not None:
                    cart.is_available = True
                    cart.assigned_client = None
                print(f"client {client.id} could not start a golf round - no hole or cart available")
                client.log_activity(
                    amenity="Golf course",
                    action="Start round",
                    success=False,
                    info="No hole or cart available"
                )
                return

        # Start a golf session outside the lock
        session = GolfSession(random.randint(1, 1000), hole, client, cart)
        session.start_session()

class Hole:
    def __init__(self, id, course):
        self.id = id
        self.is_occupied = False
        self.client = None
        self.course = course

class Cart:
    def __init__(self, id):
        self.id = id
        self.is_available = True
        self.assigned_client = None

class GolfSession:
    def __init__(self, id, hole, client, cart):
        self.id = id
        self.hole = hole
        self.client = client
        self.cart = cart
        self.duration = 5  # simulate playing time in seconds

    def start_session(self):
        # Log + announce the start of the golf session
        print(f'client {self.client.id} has started a golf session on hole {self.hole.id} with cart {self.cart.id}')
        self.client.log_activity(
            amenity="Golf course",
            action="Start session",
            success=True,
            info=f"Hole {self.hole.id}, Cart {self.cart.id}, Session {self.id}"
        )

        time.sleep(self.duration)

        # After the session duration, free up the resources
        with self.hole.course.course_lock:
            self.hole.is_occupied = False
            self.hole.client = None
            self.cart.is_available = True
            self.cart.assigned_client = None

        # Log + announce end of session
        print(f'client {self.client.id} has ended a golf session on hole {self.hole.id} with cart {self.cart.id}')
        self.client.log_activity(
            amenity="Golf course",
            action="End session",
            success=True,
            info=f"Hole {self.hole.id}, Cart {self.cart.id}, Session {self.id}"
        )

class RangeSlot:
    def __init__(self, id, course):
        self.id = id
        self.is_occupied = False
        self.client = None
        self.course = course

    def practice_session(self, client, slot_id):
        # Occupy the range slot for practice
        with self.course.range_lock:
            self.is_occupied = True
            self.client = client
        print(f'client {self.client.id} has started practicing at driving range slot {slot_id}')
        client.log_activity(
            amenity="Golf driving range",
            action="Practice session start",
            success=True,
            info=f"Slot {slot_id}"
        )
        time.sleep(5)  # simulate practice time
        self.finish_practice(client, slot_id)

    def finish_practice(self, client, slot_id):
        # Free the range slot after practice
        with self.course.range_lock:
            self.is_occupied = False
            self.client = None
        print(f'client {client.id} has finished practicing at driving range slot {slot_id}')
        client.log_activity(
            amenity="Golf driving range",
            action="Practice session end",
            success=True,
            info=f"Slot {slot_id}"
        )

class Client:
    """
    Local Client used in this file for now.
    In the integrated project, this should be replaced
    by the global Client class that already defines log_activity.
    """
    def __init__(self, id, golfcourse):
        self.id = id
        self.golfcourse = golfcourse

    def log_activity(self, amenity, action, success, info=""):
        # Placeholder: in the real project the global Client will override this
        print(f"[LOG] Client {self.id} | {amenity} | {action} | success={success} | {info}")

    def go_to_golf(self):
        # Randomly decide to either practice at the range or play on the course
        coin = random.randint(1, 2)
        if coin == 1:
            self.golfcourse.practice_range(self)
        else:
            self.golfcourse.play_course(self)

def main():
    golfcourse = GolfCourse()
    # Create 9 holes
    holes = [Hole(i, golfcourse) for i in range(1, 10)]
    golfcourse.holes = holes
    # Create 5 golf carts
    carts = [Cart(i) for i in range(1, 6)]
    golfcourse.carts = carts
    # Create 5 driving range slots
    range_slots = [RangeSlot(i, golfcourse) for i in range(1, 6)]
    golfcourse.range_slots = range_slots
    # Create clients
    clients = [Client(i, golfcourse) for i in range(1, 40)]
    # Launch each client in a separate thread
    for client in clients:
        t = threading.Thread(target=client.go_to_golf)
        t.start()

if __name__ == "__main__":
    main()
