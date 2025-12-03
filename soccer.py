import random
import threading
import time

class SoccerPitch:
    def __init__(self):
        self.teamA = []
        self.teamA_lock = threading.Lock()
        self.teamB = []
        self.teamB_lock = threading.Lock()

        self.players = []
        self.match_counter = 1
        self.previous_match = 1
        self.match_counter_lock = threading.Lock()

    def join_a_team(self, client):
        with self.match_counter_lock:
            if self.match_counter >= 5:
                return

        with self.teamA_lock:
            if len(self.teamA) < 7:
                self.teamA.append(client)
                client.log_activity(
                    amenity="Soccer",
                    action="Join a Team",
                    success=True,
                    info="Joined team A"
                )
                return

        with self.teamB_lock:
            if len(self.teamB) < 7:
                self.teamB.append(client)
                client.log_activity(
                    amenity="Soccer",
                    action="Join a Team",
                    success=True,
                    info="Joined team B"
                )
                return

        print(f"Client {client.id} tried to play a soccer match, but teams are full")
        client.log_activity(
            amenity="Soccer",
            action="Join a Team",
            success=False,
            info="Teams are full"
        )
        return

    def start_match(self):

        while True:
            time.sleep(1)

            with self.match_counter_lock:

                if self.previous_match != self.match_counter:
                    break

            with self.teamA_lock:
                with self.teamB_lock:

                    if len(self.teamA) == 7 and len(self.teamB) == 7:

                        self.players = self.teamA + self.teamB

                        with self.match_counter_lock:
                            match = Match(self.teamA, self.teamB, self.match_counter, self)
                            print(f"AND MATCH {self.match_counter} BEGINS!!!!!!!")
                            self.match_counter += 1

                        timer_thread = threading.Thread(target=match.timer)
                        timer_thread.start()

                        random.shuffle(self.players)

                        for p in self.players:
                            th = threading.Thread(target=match.play, args=(p,))
                            th.start()
                        self.teamA = []
                        self.teamB = []
                        self.players = []

                        break  # End start_match loop

            time.sleep(0.2)


class Match:
    def __init__(self, teamA, teamB, match_id, soccerpitch):
        self.ball = threading.Lock()
        self.teamA = teamA
        self.teamB = teamB
        self.players = teamA + teamB
        self.teamA_score = 0
        self.teamB_score = 0
        self.going = True
        self.match_id = match_id
        self.pitch = soccerpitch

    def timer(self):
        t_end = time.time() + 10

        while time.time() < t_end:
            time.sleep(0.05)

        self.going = False
        time.sleep(1)

        print()
        print(f"END OF MATCH {self.match_id} !!!!!!!!!")
        print(f"The final score was {self.teamA_score} for team A and {self.teamB_score} for team B in match {self.match_id}")

        with self.pitch.match_counter_lock:

            self.pitch.previous_match = self.match_id

    def play(self, player):
        while self.going:
            with self.ball:
                goal = 1
                shot = random.randint(1, 100)

                if shot == goal:
                    if player in self.teamA:
                        self.teamA_score += 1
                        print(f"Client {player.id} has just scored a goal for team A")
                        print(f'The score is now {self.teamA_score} for team A and {self.teamB_score} for team B in match {self.match_id}')
                        player.log_activity(
                            amenity="Soccer",
                            action="Shot",
                            success=True,
                            info="Scored a goal for team A"
                        )
                    else:
                        self.teamB_score += 1
                        print(f"Client {player.id} has just scored a goal for team B in match {self.match_id}")
                        print(f'The score is now {self.teamA_score} for team A and {self.teamB_score} for team B in match {self.match_id}')
                        player.log_activity(
                            amenity="Soccer",
                            action="Shot",
                            success=True,
                            info="Scored a goal for team B"
                        )

            time.sleep(2)
        return
