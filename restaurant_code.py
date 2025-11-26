import random
import threading
import time


class Table:
    def __init__(self, number, capacity=5):
        self.number = number
        self.capacity = capacity
        self.is_occupied = False
        self.group_size = 0
        self.current_order = None
        self.assigned_clients = []  # Track individual clients in this group

    def occupy(self, group_size, order, clients):
        self.is_occupied = True
        self.group_size = group_size
        self.current_order = order
        self.assigned_clients = clients

    def free(self):
        self.is_occupied = False
        self.group_size = 0
        self.current_order = None
        self.assigned_clients = []


class Restaurant:
    def __init__(self):
        self.tables = [Table(i) for i in range(1, 11)]  # 10 tables
        self.tables_lock = threading.RLock()
        self.queue = []
        self.total_revenue = 0.0
        self.revenue_lock = threading.Lock()
        self.menu = {
            "Burger & Fries": 16.00,
            "Pizza": 13.00,
            "Salad": 9.00,
            "Chicken Wrap": 14.00,
            "Steak": 25.50,
            "Soda": 4.00,
            "Wine": 7.00,
            "Water": 2.00
        }

    def find_free_table(self, group_size): #find a free table
        with self.tables_lock:
            for table in self.tables:
                if not table.is_occupied and group_size <= table.capacity:
                    return table
        return None

    def dine_at_restaurant(self, client):
        """Main method for individual clients to use the restaurant - NON-BLOCKING"""
        # Individual dining - client dines alone
        while True:
            table = self.find_free_table(1)  # Look for table for 1 person
            if table:
                with self.tables_lock:
                    order = self.choose_individual_order()
                    table.occupy(1, order, [client])
                
                print(f"Client {client.id} seated at Table {table.number}")
                client.log_activity(
                    amenity="Restaurant",
                    action="Seated at table",
                    success=True,
                    info=f"Table {table.number}"
                )
                
                # Start dining session in background thread (NON-BLOCKING)
                t = threading.Thread(target=self._dining_session, args=(client, table))
                t.start()
                break
            else:
                with self.tables_lock:
                    if client not in self.queue:
                        self.queue.append(client)
                        print(f"Client {client.id} waiting in restaurant queue ({len(self.queue)} waiting)")
                        client.log_activity(
                            amenity="Restaurant",
                            action="Join queue",
                            success=True,
                            info=f"Queue position: {len(self.queue)}"
                        )
                time.sleep(2)

    def choose_individual_order(self):
        """Choose order for individual client"""
        order = {}
        num_items = random.randint(1, 3)  # 1-3 items per person
        for _ in range(num_items):
            item = random.choice(list(self.menu.keys()))
            order[item] = order.get(item, 0) + 1
        return order

    def _dining_session(self, client, table):
        """Handle the dining session in a separate thread - NON-BLOCKING"""
        # Simulate eating time
        eat_time = random.randint(3, 8)
        time.sleep(eat_time)

        total = 0
        print(f"Client {client.id} finished eating at Table {table.number}")
        print("Order summary:")
        for item, qty in table.current_order.items():
            price = self.menu[item]
            subtotal = price * qty
            total += subtotal
            print(f"   {item} x{qty} = ${subtotal:.2f}")

        print(f" Total bill: ${total:.2f}")
        
        with self.revenue_lock:
            self.total_revenue += total

        # Log the dining experience
        client.log_activity(
            amenity="Restaurant",
            action="Finish dining",
            success=True,
            info=f"Table {table.number}, Bill: ${total:.2f}, Duration: {eat_time}s"
        )

        with self.tables_lock:
            table.free()
            print(f"Table {table.number} is now free.")

            # Seat next waiting client if any
            if self.queue:
                next_client = self.queue.pop(0)
                print(f"Seating next in queue: Client {next_client.id}")
                # Start new dining session for next client
                threading.Thread(target=self._dining_session, args=(next_client, table)).start()