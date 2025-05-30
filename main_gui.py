import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext
import sys
import io
import threading

from games.flappy.visualizer import VisualTrainer as FlappyTrainer
from games.flappy.game import FlappyGame

from games.dino.visualizer import DinoVisualizer as DinoTrainer
from games.dino.game import DinoGame

from core.multi_train import multi_train    
import tkinter as tk
from core.experiments.multi_experiment_visualizer import MultiExperimentVisualizer, ExperimentConfig



class GenPlayApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GenPlay - Neuroevolution Game Trainer")
        self.root.geometry("400x300")

        self.main_menu()

    def main_menu(self):
        self.clear_window()
        self.root.geometry("400x300")
        tk.Label(self.root, text="Select Game", font=("Arial", 18)).pack(pady=20)

        tk.Button(self.root, text="Flappy Bird", width=20, command=self.flappy_menu).pack(pady=5)
        tk.Button(self.root, text="Dino Runner", width=20, command=self.dino_menu).pack(pady=5)
        tk.Button(self.root, text="Multi-game Training", width=20, command=self.run_multi_game).pack(pady=5)
        tk.Button(self.root, text="Exit", width=20, command=self.root.quit).pack(pady=20)

    def flappy_menu(self):
        self.game_mode_menu("flappy", FlappyGame, FlappyTrainer)

    def dino_menu(self):
        self.game_mode_menu("dino", DinoGame, DinoTrainer)

    def game_mode_menu(self, game_name, GameClass, TrainerClass):
        self.clear_window()
        self.root.geometry("400x300")
        tk.Label(self.root, text=f"{game_name.capitalize()} - Select Mode", font=("Arial", 16)).pack(pady=20)

        tk.Button(self.root, text="Play manually", width=25, command=lambda: GameClass().run()).pack(pady=5)
        tk.Button(self.root, text="Train agents", width=25, command=lambda: TrainerClass().run()).pack(pady=5)
        tk.Button(self.root, text="Watch best agent", width=25, command=lambda: TrainerClass().watch_best()).pack(pady=5)
        tk.Button(self.root, text="Compare experiments", width=25, command=lambda: self.experiment_setup(game_name, GameClass, TrainerClass)).pack(pady=5)
        tk.Button(self.root, text="Back", width=25, command=self.main_menu).pack(pady=20)

    def run_multi_game(self):
        self.clear_window()
        self.root.geometry("400x350")

        tk.Label(self.root, text="Multi-game Training (Flappy + Dino)", font=("Arial", 14)).pack(pady=5)
        log_box = scrolledtext.ScrolledText(self.root, width=60, height=15, state='disabled', font=("Courier", 10))
        log_box.pack(pady=10)

        tk.Button(self.root, text="Back to Main Menu", command=self.main_menu).pack(pady=5)

        class LogStream(io.StringIO):
            def write(inner_self, msg):
                log_box.configure(state='normal')

                if msg.endswith('\r'):
                    log_box.delete("end-2l", "end-1l")
                    msg = msg.rstrip("\r") + "\n"
                log_box.insert(tk.END, msg)
                log_box.see(tk.END)
                log_box.configure(state='disabled')
                log_box.update_idletasks()

        def start_training():
            sys.stdout = LogStream()
            try:
                multi_train()
            finally:
                sys.stdout = sys.__stdout__

        threading.Thread(target=start_training, daemon=True).start()

    def experiment_setup(self, game_type, GameClass, TrainerClass):
        self.GameClass = GameClass
        self.TrainerClass = TrainerClass
        self.setup_experiment_gui(game_type)

    def setup_experiment_gui(self, game_type):
        self.clear_window()
        self.root.geometry("400x500")

        # === MAIN LAYOUT CONTAINER ===
        outer = tk.Frame(self.root)
        outer.pack(fill="both", expand=True)

        # === Configure grid layout ===
        outer.grid_rowconfigure(1, weight=1)
        outer.grid_columnconfigure(0, weight=1)

        # === HEADER (Title + spinner) ===
        header = tk.Frame(outer)
        header.grid(row=0, column=0, sticky="ew", pady=(10, 5))

        tk.Label(header, text=f"{game_type.capitalize()} - Compare Experiments", font=("Arial", 16)).pack(pady=5)

        num_var = tk.IntVar(value=2)
        tk.Label(header, text="Number of Experiments (1-4):").pack()
        tk.Spinbox(header, from_=1, to=4, textvariable=num_var, width=5).pack()

        # === SCROLLABLE EXPERIMENTS AREA ===
        canvas_frame = tk.Frame(outer)
        canvas_frame.grid(row=1, column=0, sticky="nsew")

        canvas = tk.Canvas(canvas_frame)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        experiment_vars = []

        def render_fields():
            for widget in scrollable_frame.winfo_children():
                widget.destroy()
            experiment_vars.clear()

            for i in range(num_var.get()):
                frame = tk.LabelFrame(scrollable_frame, text=f"Experiment #{i+1}", padx=10, pady=10)
                frame.pack(fill="x", pady=5, padx=5)

                mut = tk.DoubleVar(value=0.1)
                retain = tk.DoubleVar(value=0.2)
                agents = tk.IntVar(value=50)

                tk.Label(frame, text="Mutation Rate (0.0-1.0):").grid(row=0, column=0, sticky="w")
                tk.Scale(frame, from_=0.0, to=1.0, resolution=0.01, orient="horizontal", variable=mut).grid(row=0, column=1)

                tk.Label(frame, text="Retain Top % (0.0-1.0):").grid(row=1, column=0, sticky="w")
                tk.Scale(frame, from_=0.0, to=1.0, resolution=0.01, orient="horizontal", variable=retain).grid(row=1, column=1)

                tk.Label(frame, text="Number of Agents (5-500):").grid(row=2, column=0, sticky="w")
                tk.Spinbox(frame, from_=5, to=500, textvariable=agents, width=6).grid(row=2, column=1)

                experiment_vars.append((mut, retain, agents))

        render_fields()
        num_var.trace_add("write", lambda *args: render_fields())

        # === FIXED BOTTOM BUTTONS ===
        footer = tk.Frame(outer)
        footer.grid(row=2, column=0, pady=10)

        def start_experiments():
            configs = []
            for i, (mut_var, retain_var, agents_var) in enumerate(experiment_vars):
                mut = mut_var.get()
                retain = retain_var.get()
                agents = agents_var.get()

                label = f"Mut={mut:.2f}, Top={retain:.2f}, Agents={agents}"
                configs.append(ExperimentConfig(
                    label=label,
                    mutation_rate=mut,
                    retain_top=retain,
                    num_agents=agents,
                    game_type=game_type.lower()
                ))

            from core.experiments.multi_experiment_visualizer import MultiExperimentVisualizer
            visualizer = MultiExperimentVisualizer(configs)
            visualizer.run()

        tk.Button(footer, text="Start Comparison", command=start_experiments).pack(side="left", padx=10)
        tk.Button(self.root, text="Back", command=lambda: self.game_mode_menu(game_type, self.GameClass, self.TrainerClass)).pack()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = GenPlayApp(root)
    root.mainloop()