import threading
import time
import random
from collections import deque


class PadelCourt:
    def __init__(self, id):
        self.id = id
        self.is_occupied = False
        self.players = []  # List of Client objects
        self.match_duration = 0

class PadelCourtArea:
    def __init__(self, total_courts=4):
        self.total_courts = total_courts
        self.courts = [PadelCourt(i) for i in range(1, total_courts + 1)]
        
        # RLock allows the same thread to re-acquire the lock if needed
        self.court_lock = threading.RLock()

        # Queue for solo members who arrive without partners
        self.waiting_solo_players = deque()

        # Queue for pairs (2 members ready to play)
        self.waiting_pairs = deque()

        print(f"Padel Court Area initialized with {self.total_courts} courts")

    def play_padel(self, client):
        """
        Main method for individual clients to play padel
        """
        with self.court_lock:
            # Check if client can join an existing waiting pair
            if self.waiting_solo_players:
                partner = self.waiting_solo_players.popleft()
                # Create a pair and try to get a court
                pair = [partner, client]
                self.waiting_pairs.append(pair)
                print(f"Client {client.id} paired with Client {partner.id} for padel")
                
                # ✅ LOG: Successful pairing
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
                
                # Try to assign court to the new pair
                court_assigned = self._assign_courts_to_pairs()
                if court_assigned:
                    # ✅ LOG: Court assigned from pairing
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
                # No partner available, wait in solo queue
                self.waiting_solo_players.append(client)
                print(f"Client {client.id} waiting for padel partner. Solo queue: {len(self.waiting_solo_players)}")
                
                # ✅ LOG: Joined solo queue
                client.log_activity(
                    amenity="Padel Court",
                    action="Join solo queue",
                    success=True,
                    info=f"Queue position: {len(self.waiting_solo_players)}"
                )

    def _assign_courts_to_pairs(self):
        """Assign available courts to waiting pairs - returns True if court was assigned"""
        available_court = None
        for court in self.courts:
            if not court.is_occupied:
                available_court = court
                break
        
        if available_court and self.waiting_pairs:
            pair = self.waiting_pairs.popleft()
            self._start_padel_match(available_court, pair)
            
            # ✅ LOG: Court assigned from queue
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
        """
        Start a padel match on the given court with the given players
        """
        court.is_occupied = True
        court.players = players
        court.match_duration = random.randint(3, 8)  # 3-8 seconds simulation time
        
        players_str = ", ".join([f"Client {p.id}" for p in players])
        print(f"Padel match STARTED on Court {court.id} with players: [{players_str}]")
        
        # ✅ LOG: Match started for all players
        for player in players:
            player.log_activity(
                amenity="Padel Court",
                action="Start match",
                success=True,
                info=f"Court {court.id}, Partners: {[p.id for p in players if p != player]}, Duration: {court.match_duration}s"
            )
        
        # Start match in background thread
        threading.Thread(
            target=self._run_padel_match,
            args=(court,),
            daemon=True
        ).start()

    def _run_padel_match(self, court):
        """
        Run the padel match simulation in background thread
        """
        # Simulate match duration
        time.sleep(court.match_duration)
        
        with self.court_lock:
            players_str = ", ".join([f"Client {p.id}" for p in court.players])
            print(f"Padel match COMPLETED on Court {court.id}. Players: [{players_str}]")
            
            # ✅ LOG: Match completed for all players
            for player in court.players:
                player.log_activity(
                    amenity="Padel Court",
                    action="Finish match",
                    success=True,
                    info=f"Court {court.id}, Duration: {court.match_duration}s"
                )
            
            # Free the court
            court.is_occupied = False
            court.players = []
            
            # Try to assign next waiting pairs
            court_assigned = self._assign_courts_to_pairs()
            
            # ✅ LOG: If no court available after match completion
            if not court_assigned and (self.waiting_solo_players or self.waiting_pairs):
                print(f"Court {court.id} freed but no immediate assignment - queues still active")
                # No need to log this for individual clients as they're already in queues

    def get_court_status(self):
        """
        Return current padel area status
        """
        with self.court_lock:
            occupied_courts = sum(1 for court in self.courts if court.is_occupied)
            return {
                "available_courts": self.total_courts - occupied_courts,
                "total_courts": self.total_courts,
                "waiting_solo_players": len(self.waiting_solo_players),
                "waiting_pairs": len(self.waiting_pairs),
            }