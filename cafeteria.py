import random
import threading
import time


class Client:
    def __init__(self, id):
        self.id = id

        # One dictionary per client to store everything they did
        self.history = {
            "client_id": self.id,
            "activities": []   # list of activity dicts
        }

    def log_activity(self, amenity, action, success, info=""):
        """
        Store a single activity in the client's history.
        NO TIMESTAMP (simplified)
        """
        activity = {
            "amenity": amenity,
            "action": action,
            "success": int(success),  # 1 or 0
            "info": info
        }
        self.history["activities"].append(activity)


class Cafeteria:
    def __init__(self):
        self.servers = None  # servers list
        self.menu = None     # list of FoodItems
        self.server_lock = threading.RLock()
        self.inventory_lock = threading.RLock()

    def order_at_counter(self, client):
        # Critical region: server availability
        with self.server_lock:
            server = None
            for s in self.servers:
                if s.is_available:
                    s.is_available = False
                    s.assigned_client = client
                    server = s
                    break

        if server is None:
            print(f"client {client.id} could not order as no servers are available.")

            # LOG FAILURE
            client.log_activity(
                amenity="cafeteria",
                action="order",
                success=False,
                info="no_server_available"
            )
            return

        # Client chooses 1 item from the menu
        requested_item = random.choice(self.menu)

        # LOG ATTEMPT (will finish inside ServingSession)
        client.log_activity(
            amenity="cafeteria",
            action="order_attempt",
            success=True,
            info=f"requested_{requested_item.name}"
        )

        # Start serving session
        session = ServingSession(2, client, server, requested_item, self)
        session.start_session()


class Server:
    def __init__(self, id):
        self.id = id
        self.is_available = True
        self.assigned_client = None


class FoodItem:
    def __init__(self, name, quantity):
        self.name = name
        self.quantity = quantity  # remaining portions


class ServingSession:
    def __init__(self, duration, client, server, requested_item, cafeteria):
        self.duration = duration
        self.client = client
        self.server = server
        self.requested_item = requested_item
        self.cafeteria = cafeteria

    def start_session(self):
        # Critical region: check inventory & serve
        with self.cafeteria.inventory_lock:
            if self.requested_item.quantity > 0:

                # Reserve 1 portion
                self.requested_item.quantity -= 1
                item_name = self.requested_item.name

                print(f"client {self.client.id} is being served '{item_name}' by server {self.server.id}.")
                time.sleep(self.duration)
                print(f"client {self.client.id} received '{item_name}' from server {self.server.id}.")

                # LOG SUCCESS
                self.client.log_activity(
                    amenity="cafeteria",
                    action="order",
                    success=True,
                    info=f"{item_name}_served_by_server_{self.server.id}"
                )

                self.finish_and_release_server()

                # Start eating
                eating = EatingSession(3, self.client, item_name)
                eating.start_session()
                return

            else:
                # Out of stock
                item_name = self.requested_item.name
                print(f"client {self.client.id} could not be served '{item_name}' because it is out of stock.")

                # LOG FAILURE
                self.client.log_activity(
                    amenity="cafeteria",
                    action="order",
                    success=False,
                    info=f"{item_name}_out_of_stock"
                )

        self.finish_and_release_server()

    def finish_and_release_server(self):
        with self.cafeteria.server_lock:
            self.server.is_available = True
            self.server.assigned_client = None


class EatingSession:
    def __init__(self, duration, client, item_name):
        self.duration = duration
        self.client = client
        self.item_name = item_name

    def start_session(self):
        print(f"client {self.client.id} sat down to eat '{self.item_name}'.")
        time.sleep(self.duration)
        print(f"client {self.client.id} finished eating '{self.item_name}'.")


def main():
    cafeteria = Cafeteria()

    # Create servers (critical resource)
    servers = []
    for i in range(1, 4):  # 3 servers
        servers.append(Server(i))
    cafeteria.servers = servers

    # Menu with limited stock
    cafeteria.menu = [
        FoodItem("sandwich", 10),
        FoodItem("salad", 8),
        FoodItem("pizza", 6),
        FoodItem("pasta", 5),
    ]

    # Create clients
    clients = [Client(i) for i in range(1, 31)]

    threads = []
    for c in clients:
        t = threading.Thread(target=cafeteria.order_at_counter, args=(c,))
        t.start()
        threads.append(t)

    # Wait for all threads to finish
    for t in threads:
        t.join()

    # Print client histories for debugging
    for c in clients:
        print(f"\nClient {c.id} history:")
        for activity in c.history["activities"]:
            print(activity)


if __name__ == "__main__":
    main()