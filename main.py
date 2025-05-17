import sys

from games.flappy.visualizer import VisualTrainer as FlappyTrainer
from games.flappy.game import FlappyGame

from games.dino.visualizer import DinoVisualizer as DinoTrainer
from games.dino.game import DinoGame

def prompt_game():
    print("\nSelect game:")
    print("1 - Flappy Bird")
    print("2 - Dino Runner")
    print("Q - Quit")
    choice = input("Enter your choice: ").strip().lower()
    return choice

def prompt_mode():
    print("\nSelect mode:")
    print("1 - Play manually")
    print("2 - Train agents")
    print("3 - Watch best agent so far")
    print("B - Back to game selection")
    print("Q - Quit")
    choice = input("Enter your choice: ").strip().lower()
    return choice

def run_game_menu(game_name, GameClass, TrainerClass):
    while True:
        choice = prompt_mode()

        if choice == "1":
            game = GameClass()
            game.run()

        elif choice == "2":
            trainer = TrainerClass()
            trainer.run()

        elif choice == "3":
            trainer = TrainerClass()
            trainer.watch_best()

        elif choice in ("b", "back"):
            break

        elif choice in ("q", "quit", "exit"):
            print("Exiting.")
            sys.exit(0)

        else:
            print("Invalid choice. Try again.")

def main():
    while True:
        game_choice = prompt_game()

        if game_choice == "1":
            run_game_menu("Flappy", FlappyGame, FlappyTrainer)

        elif game_choice == "2":
            run_game_menu("Dino", DinoGame, DinoTrainer)

        elif game_choice in ("q", "quit", "exit"):
            print("Exiting.")
            sys.exit(0)

        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()