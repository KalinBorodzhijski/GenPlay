import sys

from games.flappy.visualizer import VisualTrainer as FlappyTrainer
from games.flappy.game import FlappyGame

from games.dino.visualizer import DinoVisualizer as DinoTrainer
from games.dino.game import DinoGame

from core.multi_train import multi_train

from core.experiments.multi_experiment_visualizer import MultiExperimentVisualizer, ExperimentConfig

def prompt_game():
    print("\nSelect game:")
    print("1 - Flappy Bird")
    print("2 - Dino Runner")
    print("3 - Multi-game training")
    print("Q - Quit")
    choice = input("Enter your choice: ").strip().lower()
    return choice

def prompt_mode():
    print("\nSelect mode:")
    print("1 - Play manually")
    print("2 - Train agents")
    print("3 - Watch best agent")
    print("4 - Compare multiple experiments")
    print("B - Back to game selection")
    print("Q - Quit")
    return input("Enter your choice: ").strip().lower()

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

        elif choice == "4":
            run_multi_experiment(game_name.lower())

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

        elif game_choice == "3":
            print("\nStarting multi-game training...\n")
            multi_train()

        elif game_choice in ("q", "quit", "exit"):
            print("Exiting.")
            sys.exit(0)

        else:
            print("Invalid choice. Try again.")


def run_multi_experiment(game_type):
    print(f"\n--- Set up experiments for {game_type.upper()} ---")
    num = input("How many experiments? (1-4): ").strip()
    try:
        num = int(num)
        assert 1 <= num <= 4
    except:
        print("Invalid input. Must be a number between 1 and 4.")
        return

    experiments = []
    for i in range(num):
        print(f"\nExperiment #{i + 1}")
        mut = float(input("  Mutation rate (e.g. 0.1): "))
        retain = float(input("  Retain top % (e.g. 0.2): "))
        agents = int(input("  Number of agents: "))

        label = f"Mut={mut}, Top={retain}, Agents={agents}"

        if game_type == "flappy":
            experiments.append(ExperimentConfig(
                label=label,
                mutation_rate=mut,
                retain_top=retain,
                num_agents=agents,
                game_type="flappy"
            ))
        elif game_type == "dino":
            experiments.append(ExperimentConfig(
                label=label,
                mutation_rate=mut,
                retain_top=retain,
                num_agents=agents,
                game_type="dino"
            ))

    visualizer = MultiExperimentVisualizer(experiments)
    visualizer.run()

if __name__ == "__main__":
    main()