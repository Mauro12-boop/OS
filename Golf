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

    # Notice we use RLock not Lock: it allows the same thread to acquire the same lock multiple times. This means if one function (in the same thread) calls another function that also uses the same lock, it won't deadlock and can safely re-enter the lock.
    # Other threads, however, still have to wait until the lock is fully released.
    # Example: if a client finds an available range slot (using course.range_lock), it can then start practicing (which reuses course.range_lock safely).

    def practice_range(self, client):
        # Client tries to practice at the driving range
        with self.range_lock:
            slot = None
            for s in self.range_slots:
                if not s.is_occupied:
                    slot = s
                    break
        if slot:
            # If a free slot is found, start a practice session
            slot.practice_session(client, slot.id)
        else:
            # No free slot available
            print(f"client {client.id} could not practice at the driving range - all slots were full")

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
                return
        # Start a golf session outside the lock
        session = GolfSession(random.randint(1, 1000), hole, client, cart)
        session.start_session()

class Client:
    def __init__(self, id, golfcourse):
        self.id = id
        self.golfcourse = golfcourse

    def go_to_golf(self):
        # Simulate staggered arrival of clients
        time.sleep(random.uniform(0.1, 1.0))
        # Randomly decide to either practice at the range or play on the course
        coin = random.randint(1, 2)
        if coin == 1:
            self.golfcourse.practice_range(self)
        else:
            self.golfcourse.play_course(self)

##First I defined the two components a client needs to start a session: Cart and hole

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

## Now I created the actual session the client will start: 

class GolfSession:
    def __init__(self, id, hole, client, cart):
        self.id = id
        self.hole = hole
        self.client = client
        self.cart = cart
        self.duration = random.uniform(2, 4)  # shortened session duration

    def start_session(self):
        # Announce the start of the golf session
        print(f'client {self.client.id} has started a golf session on hole {self.hole.id} with cart {self.cart.id}')
        time.sleep(self.duration)
        # After the session duration, free up the resources
        with self.hole.course.course_lock:
            self.hole.is_occupied = False
            self.hole.client = None
            self.cart.is_available = True
            self.cart.assigned_client = None
        # Announce the end of the golf session
        print(f'client {self.client.id} has ended a golf session on hole {self.hole.id} with cart {self.cart.id}')

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
        time.sleep(random.uniform(1.2, 2.2))  # shorter practice time for realistic turnover
        self.finish_practice(client, slot_id)

    def finish_practice(self, client, slot_id):
        # Free the range slot after practice
        with self.course.range_lock:
            self.is_occupied = False
            self.client = None
        print(f'client {client.id} has finished practicing at driving range slot {slot_id}')

def main():
    golfcourse = GolfCourse()
    # Create 9 holes (typical golf course may have 9 or 18 holes)
    holes = [Hole(i, golfcourse) for i in range(1, 10)]
    golfcourse.holes = holes
    # Create 5 golf carts (limited number of carts available)
    carts = [Cart(i) for i in range(1, 6)]
    golfcourse.carts = carts
    # Create 5 driving range slots for practice at the driving range
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
