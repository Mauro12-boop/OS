import random
import threading
import time

class SwimmingPool:
    def __init__(self):
        self.lanes = []
        self.recreation_pool = []
        self.lanes_lock = threading.RLock()
        self.recreation_lock = threading.RLock()
        self.lanes_queue = []
        self.recreation_queue = []
        self.queue_lock = threading.RLock()

        for i in range(6): #6 lanes in total in the pool
            self.lanes.append(None)  # None means empty lane

    def enter_lane_pool(self, client, from_queue=False):
        with self.lanes_lock:
            for i in range(len(self.lanes)):
                if self.lanes[i] is None:
                    self.lanes[i] = client
                    if from_queue:
                        print(f'client {client.id} from queue has started swimming in lane {i + 1}')
                        client.log_activity(
                            amenity="Swimming Pool Lane",
                            action="Enter from queue",
                            success=True,
                            info=f"Lane {i + 1}"
                        )
                    else:
                        print(f'client {client.id} has started swimming in lane {i + 1}')
                        client.log_activity(
                            amenity="Swimming Pool Lane",
                            action="Enter lane",
                            success=True,
                            info=f"Lane {i + 1}"
                        )

                    # Start swim session in background thread
                    t = threading.Thread(target=self._lane_swim_session, args=(client, i))
                    t.start()
                    return True

        return False

    def _lane_swim_session(self, client, lane_index):
        # Swim for random time
        swim_time = random.randint(3, 8)
        time.sleep(swim_time)

        with self.lanes_lock:
            if self.lanes[lane_index] == client:
                self.lanes[lane_index] = None
        print(f'client {client.id} has finished swimming in lane {lane_index + 1}')
        client.log_activity(
            amenity="Swimming Pool Lane",
            action="Finish swimming",
            success=True,
            info=f"Lane {lane_index + 1}, Duration: {swim_time}s"
        )

        # Process queue after someone leaves
        self._process_lanes_queue()

    def enter_recreation_pool(self, client, from_queue=False):
        with self.recreation_lock:
            if len(self.recreation_pool) < 20:
                self.recreation_pool.append(client)
                if from_queue:
                    print(f'client {client.id} from queue has started swimming in recreation pool')
                    client.log_activity(
                        amenity="Swimming Pool Recreation",
                        action="Enter from queue",
                        success=True,
                        info="Recreation pool"
                    )
                else:
                    print(f'client {client.id} has started swimming in recreation pool')
                    client.log_activity(
                        amenity="Swimming Pool Recreation",
                        action="Enter recreation",
                        success=True,
                        info="Recreation pool"
                    )

                # Start swim session in background thread
                t = threading.Thread(target=self._recreation_swim_session, args=(client,))
                t.start()
                return True

        return False

    def _recreation_swim_session(self, client):
        # Swim for random time
        swim_time = random.randint(5, 10)
        time.sleep(swim_time)

        with self.recreation_lock:
            if client in self.recreation_pool:
                self.recreation_pool.remove(client)
        print(f'client {client.id} has finished swimming in recreation pool')
        client.log_activity(
            amenity="Swimming Pool Recreation",
            action="Finish swimming",
            success=True,
            info=f"Recreation pool, Duration: {swim_time}s"
        )

        # Process queue after someone leaves
        self._process_recreation_queue()

    def _process_lanes_queue(self):
        """Process lane pool queue when space becomes available"""
        with self.queue_lock:
            if self.lanes_queue:
                client = self.lanes_queue.pop(0)
                success = self.enter_lane_pool(client, from_queue=True)
                if success:
                    print(f"client {client.id} moved from lane queue to swimming")

    def _process_recreation_queue(self): # when there is a space available
        with self.queue_lock:
            if self.recreation_queue:
                client = self.recreation_queue.pop(0)
                success = self.enter_recreation_pool(client, from_queue=True)
                if success:
                    print(f"client {client.id} moved from recreation queue to swimming")

    def join_lanes_queue(self, client): # Adding client to lane pool queue
        with self.queue_lock:
            self.lanes_queue.append(client)
        print(f"client {client.id} joined lane pool queue (position: {len(self.lanes_queue)})")
        client.log_activity(
            amenity="Swimming Pool Lane",
            action="Join queue",
            success=True,
            info=f"Queue position: {len(self.lanes_queue)}"
        )

    def join_recreation_queue(self, client): # adding a client to the recreation pool queue
        with self.queue_lock:
            self.recreation_queue.append(client)
        print(f"client {client.id} joined recreation pool queue (position: {len(self.recreation_queue)})")
        client.log_activity(
            amenity="Swimming Pool Recreation",
            action="Join queue",
            success=True,
            info=f"Queue position: {len(self.recreation_queue)}"
        )

# REMOVED local Client class - now uses controller's Client