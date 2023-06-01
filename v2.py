import csv
from collections import deque

class Player:
    def __init__(self, id, name, elo=1200):
        self.id = id
        self.name = name
        self.elo = elo
        self.availability = True
        self.match_history = []

    def __str__(self):
        return self.name
    
    def calculate_elo(self, opponent, outcome, K=32):
        def _elo_expectation(player_elo, opponent_elo):
            return 1 / (1 + 10 ** ((opponent_elo - player_elo) / 400))

        def _elo_update(player_elo, expected, actual):
            return player_elo + K * (actual - expected)

        expected = _elo_expectation(self.elo, opponent.elo)
        self.elo = _elo_update(self.elo, expected, outcome)
        self.availability = True

    def record_match(self, opponent, outcome):
        match_detail = {"opponent": opponent.name, "outcome": outcome}
        self.match_history.append(match_detail)

class Match:
    def __init__(self, id, players, match_type, outcome=None):
        self.id = id
        self.players = players
        self.match_type = match_type
        self.outcome = outcome

    def record_outcome(self, outcome):
        self.outcome = outcome
        for player in self.players:
            player.match_history.append((self.id, outcome))


class Queue:
    def __init__(self):
        self.players = {}
        self.matches = []

    def load_players_from_csv(self, filepath):
        with open(filepath, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                id, name, elo = row
                player = Player(id, name, int(elo))
                self.add_player(player)

    def save_players_to_csv(self, filepath):
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            for player in self.players:
                writer.writerow([player.id, player.name, player.elo])

    def add_player(self, player):
        self.players[player.name] = player

    def remove_player(self, player_name):
        del self.players[player_name]

    def create_match(self, match_type):
        if len(self.players) < 2:
            print("Not enough players.")
            return None

        players_sorted = sorted(self.players.values(), key=lambda x: x.elo, reverse=True)
        if match_type == 'singles':
            p1, p2 = players_sorted[0], players_sorted[-1]
        elif match_type == 'doubles':
            p1, p2 = players_sorted[0], players_sorted[-1]
            p3, p4 = players_sorted[1], players_sorted[-2]
            self.remove_player(p3.name)
            self.remove_player(p4.name)

        self.remove_player(p1.name)
        self.remove_player(p2.name)
        match = Match(len(self.matches), [p1, p2], match_type, None) if match_type == 'singles' else Match(len(self.matches), [[p1, p2], [p3, p4]], match_type, None)
        self.matches.append(match)
        return match

def prompt_user(queue):
    while True:
        print("1. Add player")
        print("2. Remove player")
        print("3. Create singles match")
        print("4. Create doubles match")
        print("5. Record match outcome")
        print("6. View player stats")
        print("7. View match stats")
        print("8. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            name = input("Enter player's name: ")
            player = Player(len(queue.players), name)
            queue.add_player(player)
        elif choice == "2":
            name = input("Enter player's name to remove: ")
            player_to_remove = None
            for player in queue.players:
                if player.name == name:
                    player_to_remove = player
                    break
            if player_to_remove:
                queue.remove_player(player_to_remove)
            else:
                print("Player not found.")
        elif choice == "3":
            match = queue.create_match('singles')
            if match:
                print(f"Match created: {match.players[0].name} vs. {match.players[1].name}")
        elif choice == "4":
            match = queue.create_match('doubles')
            if match:
                print(f"Match created: {', '.join([str(p) for p in match.players[0]])} vs. {', '.join([str(p) for p in match.players[1]])}")

        elif choice == "5":
            match_id = int(input("Enter match id: "))
            if match_id not in range(len(queue.matches)):
                print("Invalid match id.")
                continue

            outcome = int(input("Enter outcome (1 for player1/team1 win, 0 for player2/team2 win): "))
            match = queue.matches[match_id]
            match.record_outcome(outcome)
            if match.match_type == 'singles':
                match.players[0].calculate_elo(match.players[1], outcome)
                match.players[1].calculate_elo(match.players[0], 1 - outcome)
            else:  # Doubles
                team1_avg_elo = sum([player.elo for player in match.players[0]]) / 2
                team2_avg_elo = sum([player.elo for player in match.players[1]]) / 2
                for player in match.players[0]:
                    player.calculate_elo(Player('temp', 'temp', team2_avg_elo), outcome)
                for player in match.players[1]:
                    player.calculate_elo(Player('temp', 'temp', team1_avg_elo), 1 - outcome)
        elif choice == "6":
            name = input("Enter player's name: ")
            player_to_view = None
            for player in queue.players:
                if player.name == name:
                    player_to_view = player
                    break
            if player_to_view:
                print(f"Stats for {player_to_view.name}:")
                print(f"ELO: {player_to_view.elo}")
                print(f"Match history: {player_to_view.match_history}")
            else:
                print("Player not found.")
        elif choice == "7":
            match_id = int(input("Enter match id: "))
            match = queue.matches[match_id]
            print(f"Match id: {match_id}")
            print(f"Players: {', '.join([str(p) for p in match.players])}")
            print(f"Outcome: {match.outcome}")
        elif choice == "8":
            break
        else:
            print("Invalid choice.")

queue = Queue()
queue.load_players_from_csv('players.csv')  # Load players from a CSV file
prompt_user(queue)
queue.save_players_to_csv('players.csv')  # Save players back to the CSV file
