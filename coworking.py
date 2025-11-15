import random
import threading
import time

class Seat:
    def __init__(self, id):
        self.id = id
        self.is_occupied = False

class QuietRoom:
    def __init__(self, id):
        self.id = id
        self.is_occupied = False
        self.reserved_by = None  # If not None, this room is reserved for a specific client ID

class CoWorkingSpace:
    def __init__(self):
        # Initialize 20 seats and 8 quiet rooms
        self.seats = [Seat(i) for i in range(1, 21)]
        self.quiet_rooms = [QuietRoom(i) for i in range(1, 9)]
        # Lock and condition for coordinating access to seats/rooms
        self.space_lock = threading.RLock()
        self.condition = threading.Condition(self.space_lock)
        # Vending machine revenue tracking
        self.revenue = 0.0
        self.revenue_lock = threading.Lock()
        self.products = [  # 10 vending machine products with prices
            ("Coffee", 1.5), ("Protein Bar", 2.5), ("Chips", 1.0),
            ("Soda", 1.2), ("Tea", 1.0), ("Sandwich", 3.5),
            ("Chocolate", 1.8), ("Water Bottle", 1.0),
            ("Fruit Juice", 2.0), ("Cookie", 1.1)
        ]
    
    def allocate_space(self, client):
        """Attempt to allocate a seat or quiet room for the arriving client. Wait if none is available."""
        with self.space_lock:
            # If the client has a reserved quiet room, go directly there
            if client.reserved_room is not None:
                room = client.reserved_room
                # Wait until the reserved room is free (should be free because no one else can use a reserved room)
                while room.is_occupied:
                    self.condition.wait()  # In case the room is occupied (e.g., by a prior session), wait
                room.is_occupied = True
                print(f"Client {client.id} with reservation enters quiet room {room.id}")
                client.current_space = ("room", room.id)
                return
            
            # Client has no reservation: try to get a seat or an unreserved quiet room
            while True:
                # Check for an available seat in the common area
                free_seat = None
                for seat in self.seats:
                    if not seat.is_occupied:
                        free_seat = seat
                        break
                if free_seat is not None:
                    # Occupy the free seat
                    free_seat.is_occupied = True
                    print(f"Client {client.id} took a seat in the common area (seat {free_seat.id})")
                    client.current_space = ("seat", free_seat.id)
                    return

                # No free seat; check for a free and unreserved quiet room
                free_room = None
                for room in self.quiet_rooms:
                    if (not room.is_occupied) and (room.reserved_by is None):
                        free_room = room
                        break
                if free_room is not None:
                    # Reserve and occupy the quiet room on the spot
                    free_room.is_occupied = True
                    free_room.reserved_by = client.id  # ← missing!

                    print(f"Client {client.id} found no seats, so they reserved and entered quiet room {free_room.id}")
                    client.current_space = ("room", free_room.id)
                    return

                # No seat or room available – wait until someone leaves (releases a resource)
                print(f"Client {client.id} has to wait (no space available)")
                self.condition.wait()  # Release lock and wait for notification
    #So what allocate does is check for a spot in both common space and QR, if available take it if not wait.

    def leave_space(self, client):
        """Free up the space occupied by the client and record a vending purchase."""
        with self.space_lock:
            space_type, space_id = client.current_space
            if space_type == "seat":
                # Free the seat with the matching ID
                for seat in self.seats:
                    if seat.id == space_id:
                        seat.is_occupied = False
                        break
                print(f"Client {client.id} left seat {space_id}")
            elif space_type == "room":
                # Free the quiet room with the matching ID
                for room in self.quiet_rooms:
                    if room.id == space_id:
                        room.is_occupied = False
                        # If this room was reserved by this client, clear the reservation after use
                        if room.reserved_by == client.id:
                            room.reserved_by = None
                        break
                print(f"Client {client.id} left quiet room {space_id}")
            # Simulate a purchase at the vending machine as the client leaves
            product, price = random.choice(self.products) #tupple unpacking, as product is a tuple with the name and price
            with self.revenue_lock:
                self.revenue += price
            print(f"Client {client.id} bought a {product} for ${price:.2f}")
            # Notify one waiting client that a space has become available
            self.condition.notify()

class Client:
    def __init__(self, id, coworking_space, reserved_room=None):
        self.id = id
        self.space = coworking_space
        self.reserved_room = reserved_room  # QuietRoom object if reserved, else None
        self.current_space = None  # Will hold a tuple ("seat"/"room", resource_id) when occupying a space

    def visit_coworking(self):
        """Thread target function for the client to use the coworking space."""
        # Try to get a seat or room (may wait if necessary)
        self.space.allocate_space(self)
        # Simulate working in the space for 1–2 seconds
        time.sleep(random.randint(1, 2))
        # Leave the space and make a vending machine purchase
        self.space.leave_space(self)

# ---- Simulation Setup & Execution ----
def main():
    coworking = CoWorkingSpace()
    clients = []
    num_clients = 40  # Total number of clients to simulate

    # Assign advance reservations for some clients (e.g., first 4 clients have reserved private rooms)
    reserved_clients = 4  # number of clients with pre-reserved rooms
    reserved_clients = min(reserved_clients, len(coworking.quiet_rooms))  # cannot exceed number of rooms
    for client_id in range(1, num_clients + 1):
        reserved_room = None
        if client_id <= reserved_clients:
            # Reserve quiet room with the same ID for this client
            room_obj = coworking.quiet_rooms[client_id - 1]
            room_obj.reserved_by = client_id
            reserved_room = room_obj
        clients.append(Client(client_id, coworking, reserved_room))

    # Start a thread for each client visiting the coworking space
    threads = []
    for client in clients:
        t = threading.Thread(target=client.visit_coworking)
        threads.append(t)
        t.start()

    # Wait for all client threads to finish
    for t in threads:
        t.join()

    # Print the total vending machine revenue at the end of the simulation
    print(f"Total vending machine revenue: ${coworking.revenue:.2f}")

# Entry point
if __name__ == "__main__":
    main()
