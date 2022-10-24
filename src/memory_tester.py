import random
import threading
import tkinter as tk
from dataclasses import dataclass
from time import sleep, time
from tkinter import ttk

from mcculw import ul
from mcculw.device_info import DaqDeviceInfo
from mcculw.device_info.dio_info import PortInfo
from mcculw.enums import DigitalIODirection, DigitalPortType, InterfaceType

from src.states import GameStates
from src.styles import GameStyles

from . import constants


@dataclass
class Sensor:
    id: int
    state: GameStates


class GUI(ttk.Frame):
    """GUI for the memory tester game."""

    def __init__(self) -> None:
        ttk.Frame.__init__(self)
        self.master.title("Repeat after me!")
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)
        self.grid(sticky=tk.NSEW)

        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        self.labels: list[ttk.Label] = []

        self.style = ttk.Style()
        self.style = GameStyles.config_styles(self.style)

        self.difficulty = tk.StringVar()
        self.remaining_lives = 3
        self.highest_score = 0
        self.score = 0
        self.sequence: list[int] = []
        self.is_running = False
        self.is_player_turn = False
        self.sensor_values: list[int] = [
            constants.SENSOR_OFF
        ] * constants.NUM_SENSORS

        self.sensors: list[Sensor] = [
            Sensor(id=i, state=GameStates.Neutral)
            for i in range(constants.NUM_SENSORS)
        ]

        self.create_panes()
        self.grid_panes()
        self.populate_sensors_pane()
        self.populate_info_pane()

    def generate_sequence(self) -> None:
        random.seed(time())
        self.sequence.append(random.randint(0, constants.NUM_SENSORS - 1))

    def game_logic(self):
        while self.is_running:
            if self.is_player_turn:
                continue

            self.generate_sequence()
            for id in self.sequence:
                if not self.is_running:
                    break

                self.flash_style(id=id, state=GameStates.Guess)
                sleep(constants.SLEEP_TIME)

            if not self.is_running:
                break

            self.is_player_turn = True
            self.read_player_inputs()

            if not self.remaining_lives > 0:
                self.start_stop_game()

            print(f"NEW LEVEL {self.sequence=}")

    def read_player_inputs(self):
        max_indx = len(self.sequence)
        indx = 0
        last_interaction_time = time()
        boost = int(self.difficulty.get())
        grace_period = None

        while self.is_player_turn and self.remaining_lives > 0:
            if not self.is_running:
                return

            if indx >= max_indx:
                self.gain_points(pts=10 * boost, is_level_up=True)
                break

            guesses: set[int] = set()
            try:
                target = self.sequence[indx]
            except IndexError:
                target = None

            for i, val in enumerate(self.sensor_values):
                if val == constants.SENSOR_ON:
                    guesses.add(i)

            idle_time = time() - last_interaction_time
            if not guesses:
                if idle_time > 5:
                    self.lose_a_life(msg="Inactivity")
                    last_interaction_time = time()
                continue

            last_interaction_time = time()
            if target in guesses and len(guesses) < 3:
                self.gain_points(2 * boost)
                self.flash_style(id=target, state=GameStates.Correct)
                sleep(constants.SLEEP_TIME * 2)
                indx += 1
                continue

            ths: list[threading.Thread] = []
            for id in guesses:
                th = threading.Thread(
                    target=self.flash_style, args=(id, GameStates.Incorrect)
                )
                ths.append(th)
                th.start()

            for th in ths:
                th.join()

            if not grace_period:
                self.lose_a_life(msg="Incorrect")
                grace_period = time()
                continue

            if time() - grace_period < 3:
                continue

            self.lose_a_life(msg="Incorrect")
            grace_period = time()

        self.is_player_turn = False

    def lose_a_life(self, msg: str):
        self.remaining_lives -= 1
        print(self.remaining_lives)
        self.lbl_lives.configure(
            text=f"Remaining lives: {self.remaining_lives} [{msg}]"
        )

    def gain_points(self, pts: int, is_level_up: bool = False):
        self.score += pts
        self.lbl_score.configure(text=f"Score: {self.score:5}")
        if is_level_up:
            self.lbl_lives.configure(
                text=(
                    f"Remaining lives: {self.remaining_lives}"
                    f"/ Level {len(self.sequence) + 1}"
                )
            )

    def create_panes(self) -> None:
        """Creates the different panes and store them as instance variables"""

        self.sensors_pane = ttk.Frame(self)
        self.info_pane = ttk.Frame(self)

    def grid_panes(self):
        self.info_pane.grid(sticky=tk.NSEW)
        self.sensors_pane.grid(sticky=tk.NSEW)

        for i in range(3):
            self.sensors_pane.rowconfigure(i, weight=1)
            self.info_pane.rowconfigure(i, weight=1)
            self.sensors_pane.columnconfigure(i, weight=1)
            self.info_pane.columnconfigure(i, weight=1)

    def populate_sensors_pane(self):
        for row in range(3):
            for col in range(3):
                sensor_id = col + row * 3
                lbl_name = f"Sensor {sensor_id + 1}"
                # lbl_name = f"Sensor {sensor_id}"
                style_name = f"{sensor_id}.Sensors.TLabel"
                lbl = ttk.Label(
                    self.sensors_pane,
                    text=lbl_name,
                    style=style_name,
                    anchor=tk.CENTER,
                )
                lbl.grid(
                    row=row,
                    column=col,
                    padx=constants.BW_ELEMENT_PADDING,
                    pady=constants.BW_ELEMENT_PADDING,
                    sticky=tk.NSEW,
                )
                self.labels.append(lbl)

    def populate_info_pane(self):
        # ROW 0
        self.lbl_lives = ttk.Label(
            self.info_pane,
            text=(
                f"Remaining lives: {self.remaining_lives}"
                f"/ Level {len(self.sequence) + 1}"
            ),
            anchor=tk.CENTER,
        )
        self.lbl_lives.grid(row=0, column=0, columnspan=3, sticky=tk.EW)

        with open("max_score.txt") as file:
            try:
                last_max = int(file.readline())
            except ValueError:
                last_max = 0
        self.lbl_high_score = ttk.Label(
            self, text=f"Highest score: {last_max:5}"
        )
        self.lbl_high_score.grid(row=0, column=0, sticky=tk.NW)

        # ROW 1
        self.lbl_score = ttk.Label(
            self.info_pane, text=f"Score: {self.score:5}"
        )
        self.lbl_score.grid(row=1, column=0, sticky=tk.W)

        lbl_diff = ttk.Label(self.info_pane, text="Change difficulty:   ")
        lbl_diff.grid(row=1, column=0, sticky=tk.E)

        values = [1, 2, 3, 4, 5]
        self.scale_difficulty = ttk.OptionMenu(
            self.info_pane,
            self.difficulty,
            values[2],
            *values,
        )
        self.scale_difficulty.grid(row=1, column=0, sticky=tk.E)

        self.btn_start = ttk.Button(
            self.info_pane,
            text="Start",
            padding=constants.BW_ELEMENT_PADDING,
            command=self.start_stop_game,
        )
        self.btn_start.grid(row=1, column=1, sticky=tk.E)

    def start_stop_game(self):
        if not self.is_running:
            self.is_running = True
            self.is_player_turn = False
            self.score = 0
            self.sequence: list[int] = []
            self.remaining_lives = 3
            self.style.configure("TButton", foreground="red")
            self.btn_start.configure(text="End")
            self.lbl_lives.configure(
                text=(
                    f"Remaining lives: {self.remaining_lives}"
                    f"/ Level {len(self.sequence) + 1}"
                )
            )
            threading.Thread(target=self.game_logic, daemon=True).start()
            return

        self.is_running = False
        self.style.configure("TButton", foreground="black")

        record_breaker = self.save_highest_score(score=self.score)
        new_lbl_text = (
            f"You just sat the new highest score of {self.score}!"
            if record_breaker
            else f"You scored {self.score} points!"
        )
        self.lbl_high_score.configure(
            text=f"Highest score: {self.highest_score:5}"
        )

        self.lbl_lives.configure(
            text=f"{new_lbl_text} Length of your sequence was {len(self.sequence)}."
        )
        self.btn_start.configure(text="Start")

    def save_highest_score(self, score: int) -> bool:
        with open("max_score.txt") as file:
            try:
                last_max = int(file.readline())
            except ValueError:
                last_max = 0

        if score > last_max:
            with open("max_score.txt", "w") as file:
                file.write(f"{score}")
            self.highest_score = score
            return True

        self.highest_score = last_max
        return False

    def update_style(self, lbl_id: int, state: GameStates) -> None:
        lbl_style_name = f"{lbl_id}.Sensors.TLabel"

        if state is GameStates.Correct:
            bg_color = "green"
        elif state is GameStates.Incorrect:
            bg_color = "red"
        elif state is GameStates.Guess:
            bg_color = "white"
        elif state is GameStates.Neutral:
            bg_color = constants.LABEL_BG_COLOR

        self.style.configure(lbl_style_name, background=bg_color)

    def flash_style(self, id: int, state: GameStates) -> None:
        difficulty = int(self.difficulty.get())
        sleep_time = (
            constants.SLEEP_TIME * (6 - difficulty)
            if not self.is_player_turn and self.is_running
            else constants.SLEEP_TIME
        )
        self.update_style(lbl_id=id, state=state)
        sleep(sleep_time)
        self.update_style(lbl_id=id, state=GameStates.Neutral)

    def style_updater(self) -> None:
        while True:
            for sensor in self.sensors:
                self.update_style(lbl_id=sensor.id, state=sensor.state)

    def daq_setup(self):
        device_descriptors: list[
            ul.DaqDeviceDescriptor
        ] = ul.get_daq_device_inventory(interface_type=InterfaceType.USB)
        if not device_descriptors:
            raise Exception("Error: No DAQ devices found")

        board_num = 0
        ul.create_daq_device(
            board_num=board_num, descriptor=device_descriptors[0]
        )

        daq_dev_info = DaqDeviceInfo(board_num)
        if not daq_dev_info.supports_digital_io:
            raise Exception(
                "Error: The DAQ device does not support " "digital I/O"
            )

        dio_info = daq_dev_info.get_dio_info()

        # Find the ports that support input.
        ports: list[PortInfo] = [
            port for port in dio_info.port_info if port.supports_input
        ]
        if not ports:
            raise Exception(
                "Error: The DAQ device does not support " "digital input"
            )

        # If the port is configurable, configure it for input.
        port = ports[0]
        if port.is_port_configurable:
            ul.d_config_port(board_num, port.type, DigitalIODirection.IN)

        sensor_reader = threading.Thread(
            target=self.sensor_scanner, args=(board_num, port), daemon=True
        )
        sensor_reader.start()

    def run(self):
        self.daq_setup()
        self.mainloop()

    def sensor_scanner(self, board_num: int, port: DigitalPortType) -> None:
        while True:
            self.sensor_values = self.read_sensors(
                board_num=board_num, port=port
            )

            if not self.is_running:
                for id, val in enumerate(self.sensor_values):
                    if val != constants.SENSOR_ON:
                        continue

                    self.flash_style(id=id, state=GameStates.Guess)
                sleep(constants.SLEEP_TIME)
                continue

            print(self.sensor_values)

    def read_sensors(
        self, board_num: int, port: DigitalPortType
    ) -> list[int]:
        return [
            ul.d_bit_in(
                board_num=board_num, port_type=port.type, bit_num=bit_num
            )
            for bit_num in range(constants.NUM_SENSORS)
        ]


def main():
    game = GUI()
    game.run()


if __name__ == "__main__":
    main()
