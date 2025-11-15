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

    def join_a_team(self,client):
        with self.teamA_lock:
            if len(self.teamA)<7:
                self.teamA.append(client)
                return

        with self.teamB_lock:
            if len(self.teamB)<7:
                self.teamB.append(client)
                return
        print(f"Client {client.id} tried to play a soccer match, but teams are full")

    def start_match(self):
        with self.teamA_lock and self.teamB_lock:
            if len(self.teamA)==7 and len(self.teamB)==7:
                self.players = self.teamA + self.teamB
                match = Match(self.teamA,self.teamB)
                print("AND MATCH BEGINS!!!!!!!")

                timer_thread = threading.Thread(target=match.timer)
                timer_thread.start()

                random.shuffle(self.players)
                for p in self.players:
                    p = threading.Thread(target=match.play, args = (p,))
                    p.start()

class Match:
    def __init__(self,teamA,teamB):
        self.ball = threading.Lock()
        self.teamA = teamA
        self.teamB = teamB
        self.players = teamA + teamB
        self.teamA_score = 0
        self.teamB_score = 0
        self.going = True

    def timer(self):
        t_end = time.time() + 90
        while time.time() < t_end:
            pass

        self.going = False
        time.sleep(2)
        print()
        print("END OF MATCH!!!!!!!!!")
        print(f"The final score was {self.teamA_score} for team A and {self.teamB_score} for team B")

    def play(self,player):
        while self.going:
            with self.ball:
                goal = 1
                shot = random.randint(1,100)
                if shot == goal:
                    if player in self.teamA:
                        self.teamA_score = self.teamA_score + 1
                        print(f"Client {player.id} has just scored a goal for team A")
                        print(f'The score is now {self.teamA_score} for team A and {self.teamB_score} for team B')
                    else:
                        self.teamB_score = self.teamB_score + 1
                        print(f"Client {player.id} has just scored a goal for team B")
                        print(f'The score is now {self.teamA_score} for team A and {self.teamB_score} for team B')
            time.sleep(2)
        return


class Client:
    def __init__(self,id,soccerpitch):
        self.id = id
        self.soccerpitch = soccerpitch

    def request_a_match(self):
        self.soccerpitch.join_a_team(self)


def main():

    soccerpitch = SoccerPitch()

    clients = [Client(i, soccerpitch) for i in range(1, 20)]

    for i in clients:
        t = threading.Thread(target=i.request_a_match)
        t.start()

    soccerpitch.start_match()

if __name__ == "__main__":
    main()
























