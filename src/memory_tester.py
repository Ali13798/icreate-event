import tkinter as tk
from tkinter import ttk

from src.styles import GameStyles

from . import constants


class GUI(ttk.Frame):
    """GUI for the memory tester game."""

    def __init__(self) -> None:
        ttk.Frame.__init__(self)
        self.master.title("Memory Tester")
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)
        self.grid(sticky=tk.NSEW)

        for i in range(3):
            self.rowconfigure(i, weight=1)
            self.columnconfigure(i, weight=1)

        self.labels: list[ttk.Label] = []

        self.style = ttk.Style()
        self.style = GameStyles.config_styles(self.style)

        self.create_labels_grid()

    def create_labels_grid(self):
        for row in range(3):
            for col in range(3):
                sensor_id = col + row * 3 + 1
                lbl_name = f"Sensor {sensor_id}"
                style_name = f"S{sensor_id}.TLabel"
                lbl = ttk.Label(
                    self, text=lbl_name, style=style_name, anchor=tk.CENTER
                )
                padding_value = 3
                lbl.grid(
                    row=row,
                    column=col,
                    padx=padding_value,
                    pady=padding_value,
                    sticky=tk.NSEW,
                )
                self.labels.append(lbl)


    def run(self):
        self.mainloop()


def main():
    game = GUI()
    game.run()


if __name__ == "__main__":
    main()