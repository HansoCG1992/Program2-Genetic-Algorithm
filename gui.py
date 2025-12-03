"""
GUI for the Genetic Algorithm Course Scheduler using Tkinter and Matplotlib.
Created by: Cole Hanson
"""

import tkinter as tk
from tkinter import ttk
import threading
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from genetic_scheduler import run_genetic_algorithm

class GA_GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Genetic Algorithm Course Scheduler")

        # Header
        self.label = ttk.Label(root, text="Genetic Scheduler GUI", font=("Arial", 16))
        self.label.pack(pady=10)

        # Run button
        self.run_button = tk.Button(root, text="Run Scheduler", bg="#28a745", fg="white",
                            font=("Arial", 12, "bold"),
                            command=self.start_ga_thread)
        self.run_button.pack(pady=10)

        # Status
        self.status = ttk.Label(root, text="Idle...", font=("Arial", 12))
        self.status.pack(pady=5)

        # Graph figure
        self.fig = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Fitness Over Generations")
        self.ax.set_xlabel("Generation")
        self.ax.set_ylabel("Fitness")
        self.ax.set_ylim(0, 15)


        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack()

        # Data containers
        self.gens = []
        self.best = []
        self.avg = []
        self.worst = []

    def start_ga_thread(self):
        self.status.config(text="Running...")
        thread = threading.Thread(target=self.run_ga)
        thread.daemon = True
        thread.start()

    def run_ga(self):
        # Run GA but intercept the chart updates by patching the chart printer
        import genetic_scheduler as ga

        # Patch print_fitness_chart to update the GUI instead of CLI
        def gui_chart(gens, best, avg, worst):
            self.gens = gens
            self.best = best
            self.avg = avg
            self.worst = worst

            self.update_plot()

            # Force Tkinter to refresh NOW
            self.root.update_idletasks()
            self.root.update()


        ga.print_fitness_chart = gui_chart

        # Run the GA normally
        run_genetic_algorithm()

        self.status.config(text="Done!")

    def update_plot(self):
        self.ax.clear()
        self.ax.set_title("Fitness Over Generations")
        self.ax.set_xlabel("Generation")
        self.ax.set_ylabel("Fitness")

        # Plot first (matplotlib will auto-scale, but we override after)
        self.ax.plot(self.gens, self.best, label="Best", color="green")
        self.ax.plot(self.gens, self.avg, label="Average", color="blue")
        self.ax.plot(self.gens, self.worst, label="Worst", color="red")

        # NOW override the Y scale AFTER plotting
        self.ax.set_ylim(-10, 15)   # clean, readable, never overridden

        # Set ticks every 2 units for clarity
        self.ax.set_yticks(range(-10, 16, 2))

        self.ax.legend()
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = GA_GUI(root)
    root.mainloop()
