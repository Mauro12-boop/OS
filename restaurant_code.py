 import random
import threading
import time


class Table:
    def _init_(self, number, capacity=5):
        self.number = number
        self.capacity = capacity
        self.is_occupied = False
        self.group_size = 0
        self.current_order = None

    def occupy(self, group_size, order):
        self.is_occupied = True
        self.group_size = group_size
        self.current_order = order

    def free(self):
        self.is_occupied = False
        self.group_size = 0
        self.current_order = None


class CustomerGroup:
    def _init_(self, group_id, size, restaurant):
        self.group_id = group_id
        self.size = size
        self.restaurant = restaurant

    def choose_order(self):
        order = {}
        for _ in range(self.size):
            item = random.choice(list(self.restaurant.menu.keys()))
            order[item] = order.get(item, 0) + 1
        return order

class Restaurant:
    def _init_(self):
        self.tables = [Table(i) for i in range(1, 11)]  # 10 tables
        self.tables_lock = threading.RLock()
        self.queue = []
        self.total_revenue = 0.0
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

    def seat_group(self, group): # trying to seat or queue them if full
        while True:
            table = self.find_free_table(group.size)
            if table:
                with self.tables_lock:
                    order = group.choose_order()
                    table.occupy(group.size, order)
                print(f"\n Group {group.group_id} ({group.size} people) seated at Table {table.number}")
                self.serve_table(group, table)
                break
            else:
                with self.tables_lock:
                    if group not in self.queue:
                        self.queue.append(group)
                        print(f" Group {group.group_id} waiting in queue ({len(self.queue)} waiting)")
                time.sleep(2)

    def serve_table(self, group, table): #members are dining and then they pay their bill
        time.sleep(random.randint(3, 15))  # simulate eating time

        total = 0
        print(f"\n Group {group.group_id} finished eating at Table {table.number}")
        print("Order summary:")
        for item, qty in table.current_order.items():
            price = self.menu[item]
            subtotal = price * qty
            total += subtotal
            print(f"   {item} x{qty} = ${subtotal:.2f}")

        print(f" Total bill: ${total:.2f}")
        self.total_revenue += total

        with self.tables_lock:
            table.free()
            print(f"Table {table.number} is now free.")

            # Seat next waiting group if any
            if self.queue:
                next_group = self.queue.pop(0)
                print(f"️ Seating next in queue: Group {next_group.group_id}")
                threading.Thread(target=self.seat_group, args=(next_group,)).start()

    def run_simulation(self, num_groups=30): # restaurant  #this will be changed to random according with the users in country club
        groups = [CustomerGroup(i, random.randint(1, 5), self) for i in range(1, num_groups + 1)]
        threads = []

        for group in groups:
            t = threading.Thread(target=self.seat_group, args=(group,))
            threads.append(t)
            t.start()
            time.sleep(random.uniform(0.5, 1.5))  # stagger arrivals

        for t in threads:
            t.join()

        print("\nRestaurant simulation complete!")
        print(f"Total revenue: ${self.total_revenue:.2f}")


if _name_ == "_main_":
    restaurant = Restaurant()
    restaurant.run_simulation()