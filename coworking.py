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
        self.reserved_by = None  # If not None, reserved for a specific client ID

class CoWorkingSpace:
    def __init__(self):
        self.seats = [Seat(i) for i in range(1, 21)]
        self.quiet_rooms = [QuietRoom(i) for i in range(1, 9)]
        self.space_lock = threading.RLock()
        self.condition = threading.Condition(self.space_lock)
        self.revenue = 0.0
        self.revenue_lock = threading.Lock()
        self.products = [
            ("Coffee", 1.5), ("Protein Bar", 2.5), ("Chips", 1.0),
            ("Soda", 1.2), ("Tea", 1.0), ("Sandwich", 3.5),
            ("Chocolate", 1.8), ("Water Bottle", 1.0),
            ("Fruit Juice", 2.0), ("Cookie", 1.1)
        ]

    def allocate_space(self, client):
        with self.space_lock:
            # If the client has a reserved quiet room, go directly there
            if client.reserved_room is not None:
                room = client.reserved_room
                while room.is_occupied:
                    client.log_activity(
                        amenity="Coworking quiet room",
                        action="Wait for reserved room",
                        success=True,
                        info=f"Room {room.id} currently occupied"
                    )
                    self.condition.wait()
                room.is_occupied = True
                print(f"Client {client.id} with reservation enters quiet room {room.id}")
                client.log_activity(
                    amenity="Coworking quiet room",
                    action="Enter reserved room",
                    success=True,
                    info=f"Room {room.id}"
                )
                client.current_space = ("room", room.id)
                return

            # No reservation: try to get a seat or unreserved room
            while True:
                # Check for free seat
                free_seat = None
                for seat in self.seats:
                    if not seat.is_occupied:
                        free_seat = seat
                        break
                if free_seat is not None:
                    free_seat.is_occupied = True
                    print(f"Client {client.id} took a seat in the common area (seat {free_seat.id})")
                    client.log_activity(
                        amenity="Coworking seat",
                        action="Take seat",
                        success=True,
                        info=f"Seat {free_seat.id}"
                    )
                    client.current_space = ("seat", free_seat.id)
                    return

                # No free seat; check for free, unreserved quiet room
                free_room = None
                for room in self.quiet_rooms:
                    if (not room.is_occupied) and (room.reserved_by is None):
                        free_room = room
                        break
                if free_room is not None:
                    # Reserve and occupy
                    free_room.reserved_by = client.id
                    free_room.is_occupied = True
                    print(f"Client {client.id} found no seats, so they reserved and entered quiet room {free_room.id}")
                    client.log_activity(
                        amenity="Coworking quiet room",
                        action="Reserve and enter room",
                        success=True,
                        info=f"Room {free_room.id}"
                    )
                    client.current_space = ("room", free_room.id)
                    return

                # Otherwise, must wait
                print(f"Client {client.id} has to wait (no space available)")
                client.log_activity(
                    amenity="Coworking space",
                    action="Wait for space",
                    success=True,
                    info="No seats or rooms available"
                )
                self.condition.wait()

    def leave_space(self, client):
        with self.space_lock:
            space_type, space_id = client.current_space

            if space_type == "seat":
                for seat in self.seats:
                    if seat.id == space_id:
                        seat.is_occupied = False
                        break
                print(f"Client {client.id} left seat {space_id}")
                client.log_activity(
                    amenity="Coworking seat",
                    action="Leave seat",
                    success=True,
                    info=f"Seat {space_id}"
                )
            elif space_type == "room":
                for room in self.quiet_rooms:
                    if room.id == space_id:
                        room.is_occupied = False
                        if room.reserved_by == client.id:
                            room.reserved_by = None
                        break
                print(f"Client {client.id} left quiet room {space_id}")
                client.log_activity(
                    amenity="Coworking quiet room",
                    action="Leave room",
                    success=True,
                    info=f"Room {space_id}"
                )

            # Vending machine purchase on exit
            product, price = random.choice(self.products)
            with self.revenue_lock:
                self.revenue += price
            print(f"Client {client.id} bought a {product} for ${price:.2f}")
            client.log_activity(
                amenity="Coworking vending",
                action="Purchase",
                success=True,
                info=f"Item: {product}, Price: {price:.2f}"
            )

            # Notify someone waiting
            self.condition.notify()

# REMOVED local Client class - now uses controller's Client