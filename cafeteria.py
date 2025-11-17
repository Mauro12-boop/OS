import random
import threading
import time

class Cafeteria:
    def __init__(self):
        self.servers = None #servers
        self.menu = None #FoodItems
        self.server_lock = threading.RLock()
        self.inventory_lock = threading.RLock()

    def order_at_counter(self, client):
        #critical region: server availability
        with self.server_lock:
            server = None
            for s in self.servers:
                if s.is_available:
                    s.is_available = False
                    s.assigned_client = client
                    server = s
                    break

        if server is None: #all servers were busy when this client arrived
            print(f"client {client.id} could not order as no servers are available.")
            return

        #start serving
        #Clients choose 1 item from menu
        requested_item = random.choice(self.menu)
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
        self.quantity = quantity   #remaining portions


class ServingSession:
    def __init__(self, duration, client, server, requested_item, cafeteria):
        self.duration = duration      #time to serve
        self.client = client
        self.server = server
        self.requested_item = requested_item
        self.cafeteria = cafeteria

    def start_session(self):
        #to serve the requested item (critical region: inventory)
        with self.cafeteria.inventory_lock:
            if self.requested_item.quantity > 0:
                self.requested_item.quantity -= 1 #reserve 1 portion
                item_name = self.requested_item.name
                print(f"client {self.client.id} is being served '{item_name}' by server {self.server.id}.")
                time.sleep(self.duration) #simulate serving time
                print(f"client {self.client.id} received '{item_name}' from server {self.server.id}.")
                self.finish_and_release_server() # Release server
                # Start eating
                eating = EatingSession(3, self.client, item_name)
                eating.start_session()
                return
            else: #out of stock
                item_name = self.requested_item.name
                print(f"client {self.client.id} could not be served '{item_name}' because it is out of stock.")

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


class Client:
    def __init__(self, id, cafeteria):
        self.id = id
        self.cafeteria = cafeteria

    def gocafeteria(self):
        self.cafeteria.order_at_counter(self)


def main():
    cafeteria = Cafeteria()
    servers = [] #create servers (critical resource)
    for i in range(1, 4):  # 3 servers
        servers.append(Server(i))
    cafeteria.servers = servers

    #menu with limited stock (critical resource)
    cafeteria.menu = [
        FoodItem("sandwich", 10),
        FoodItem("salad", 8),
        FoodItem("pizza", 6),
        FoodItem("pasta", 5),
    ]

    #create clients and start threads
    clients = [Client(i, cafeteria) for i in range(1, 31)]
    for c in clients:
        t = threading.Thread(target=c.gocafeteria)
        t.start()


if __name__ == "__main__":
    main()