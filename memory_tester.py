import tkinter as tk
from tkinter import ttk


class GUI(ttk.Frame):
    """GUI for the memory tester game."""

    def __init__(self) -> None:
        ttk.Frame.__init__(self)
        self.master.title("Memory Tester")
        self.grid()
