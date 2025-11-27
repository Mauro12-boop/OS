import threading
import time
import random
from collections import deque


class PadelCourt:
    def __init__(self, id):
        self.id = id
        self.is_occupied = False
        self.players = []
        self.match_duration = 0


class PadelCourtArea:
    def __init__(self, total_courts=4):
        self.total_courts = total_courts
        self.courts = [PadelCourt(i) for i in range(1, total_courts + 1)]
        self.court_lock = threading.RLock()
        self.waiting_solo_players = deque()
        self.waiting_pairs = deque()

        print(f"Padel Court Area initialized with {self.total_courts} courts")

    def play_padel(self, client):
        with self.court_lock:
            if self.waiting_solo_players:
                partner = self.waiting_solo_players.popleft()
                pair = [partner, client]
                self.waiting_pairs.append(pair)
                print(f"Client {client.id} paired with Client {partner.id} for padel")

                client.log_activity(
                    amenity="Padel Court",
                    action="Paired with player",
                    success=True,
                    info=f"Paired with Client {partner.id}"
                )
                partner.log_activity(
                    amenity="Padel Court",
                    action="Paired with player",
                    success=True,
                    info=f"Paired with Client {client.id}"
                )

                court_assigned = self._assign_courts_to_pairs()
                if court_assigned:
                    client.log_activity(
                        amenity="Padel Court",
                        action="Court assigned from pairing",
                        success=True,
                        info="Immediate court assignment after pairing"
                    )
                    partner.log_activity(
                        amenity="Padel Court",
                        action="Court assigned from pairing",
                        success=True,
                        info="Immediate court assignment after pairing"
                    )
            else:
                self.waiting_solo_players.append(client)
                print(f"Client {client.id} waiting for padel partner. Solo queue: {len(self.waiting_solo_players)}")

                client.log_activity(
                    amenity="Padel Court",
                    action="Join solo queue",
                    success=True,
                    info=f"Queue position: {len(self.waiting_solo_players)}"
                )

    def _assign_courts_to_pairs(self):
        available_court = None
        for court in self.courts:
            if not court.is_occupied:
                available_court = court
                break

        if available_court and self.waiting_pairs:
            pair = self.waiting_pairs.popleft()
            self._start_padel_match(available_court, pair)

            for player in pair:
                player.log_activity(
                    amenity="Padel Court",
                    action="Court assigned from queue",
                    success=True,
                    info=f"Court {available_court.id}"
                )
            return True
        return False

    def _start_padel_match(self, court, players):
        court.is_occupied = True
        court.players = players
        court.match_duration = random.randint(3, 8)

        players_str = ", ".join([f"Client {p.id}" for p in players])
        print(f"Padel match STARTED on Court {court.id} with players: [{players_str}]")

        for player in players:
            player.log_activity(
                amenity="Padel Court",
                action="Start match",
                success=True,
                info=f"Court {court.id}, Partners: {[p.id for p in players if p != player]}, Duration: {court.match_duration}s"
            )

        threading.Thread(
            target=self._run_padel_match,
            args=(court,),
            daemon=True
        ).start()

    def _run_padel_match(self, court):
        time.sleep(court.match_duration)

        with self.court_lock:
            players_str = ", ".join([f"Client {p.id}" for p in court.players])
            print(f"Padel match COMPLETED on Court {court.id}. Players: [{players_str}]")

            for player in court.players:
                player.log_activity(
                    amenity="Padel Court",
                    action="Finish match",
                    success=True,
                    info=f"Court {court.id}, Duration: {court.match_duration}s"
                )

            court.is_occupied = False
            court.players = []

            court_assigned = self._assign_courts_to_pairs()

            if not court_assigned and (self.waiting_solo_players or self.waiting_pairs):
                print(f"Court {court.id} freed but no immediate assignment - queues still active")



