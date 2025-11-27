import threading
import time
import random
from collections import deque


class TennisCourt:
    def __init__(self, id):
        self.id = id
        self.is_occupied = False
        self.players = []
        self.match_duration = 0


class TennisCourtArea:
    def __init__(self, total_courts=4):
        self.total_courts = total_courts
        self.courts = [TennisCourt(i) for i in range(1, total_courts + 1)]
        self.court_lock = threading.RLock()
        self.waiting_solo_players = deque()
        self.waiting_pairs = deque()

        print(f"Tennis Court Area initialized with {self.total_courts} courts")

    def play_tennis(self, client):
        with self.court_lock:
            if self.waiting_solo_players:
                partner = self.waiting_solo_players.popleft()
                pair = [partner, client]
                self.waiting_pairs.append(pair)
                print(f"Client {client.id} paired with Client {partner.id} for tennis")

                client.log_activity(
                    amenity="Tennis Court",
                    action="Paired with player",
                    success=True,
                    info=f"Paired with Client {partner.id}"
                )
                partner.log_activity(
                    amenity="Tennis Court",
                    action="Paired with player",
                    success=True,
                    info=f"Paired with Client {client.id}"
                )

                # Try to assign courts to ALL waiting pairs, not just one
                courts_assigned = self._assign_courts_to_pairs()
                if courts_assigned:
                    print(f"Assigned {courts_assigned} courts after pairing")
            else:
                self.waiting_solo_players.append(client)
                print(f"Client {client.id} waiting for tennis partner. Solo queue: {len(self.waiting_solo_players)}")

                client.log_activity(
                    amenity="Tennis Court",
                    action="Join solo queue",
                    success=True,
                    info=f"Queue position: {len(self.waiting_solo_players)}"
                )

    def _assign_courts_to_pairs(self):
        """Assign courts to as many waiting pairs as possible"""
        courts_assigned = 0

        while self.waiting_pairs:
            # Find first available court
            available_court = None
            for court in self.courts:
                if not court.is_occupied:
                    available_court = court
                    break

            if not available_court:
                break  # No more courts available

            # Assign court to the next waiting pair
            pair = self.waiting_pairs.popleft()
            self._start_tennis_match(available_court, pair)
            courts_assigned += 1

            for player in pair:
                player.log_activity(
                    amenity="Tennis Court",
                    action="Court assigned from queue",
                    success=True,
                    info=f"Court {available_court.id}"
                )

        return courts_assigned

    def _start_tennis_match(self, court, players):
        court.is_occupied = True
        court.players = players
        court.match_duration = random.randint(5, 15)

        players_str = ", ".join([f"Client {p.id}" for p in players])
        print(f"Tennis match STARTED on Court {court.id} with players: [{players_str}] for {court.match_duration}s")

        for player in players:
            partner_ids = [p.id for p in players if p != player]
            partner_info = f"Partner: {partner_ids[0]}" if partner_ids else "No partner"

            player.log_activity(
                amenity="Tennis Court",
                action="Start match",
                success=True,
                info=f"Court {court.id}, {partner_info}, Duration: {court.match_duration}s"
            )

        threading.Thread(
            target=self._run_tennis_match,
            args=(court,),
            daemon=True
        ).start()

    def _run_tennis_match(self, court):
        time.sleep(court.match_duration)

        with self.court_lock:
            players_str = ", ".join([f"Client {p.id}" for p in court.players])
            print(f"Tennis match COMPLETED on Court {court.id}. Players: [{players_str}]")

            for player in court.players:
                player.log_activity(
                    amenity="Tennis Court",
                    action="Finish match",
                    success=True,
                    info=f"Court {court.id}, Duration: {court.match_duration}s"
                )

            court.is_occupied = False
            court.players = []

            # After a match ends, try to assign courts to ALL waiting pairs
            courts_assigned = self._assign_courts_to_pairs()

            if courts_assigned:
                print(f"Assigned {courts_assigned} courts after match completion on Court {court.id}")
            elif self.waiting_solo_players or self.waiting_pairs:
                print(
                    f"Court {court.id} freed - {len(self.waiting_solo_players)} solo players and {len(self.waiting_pairs)} pairs still waiting")