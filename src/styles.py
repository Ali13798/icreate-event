from . import constants


class GameStyles:
    """Includes the style specifications of the GUI"""

    @staticmethod
    def config_styles(style) -> None:
        style.configure(
            "TButton",
            font=(None, constants.ELEMENT_FONT_SIZE),
            padding=constants.ELEMENT_PADDING,
        )

        # Configure styles - Labels
        style.configure(
            "TLabel",
            font=(None, constants.ELEMENT_FONT_SIZE),
            background=constants.FRAME_BG_COLOR,
            foreground="white",
            padding=constants.ELEMENT_PADDING,
        )

        style.configure(
            "Sensors.TLabel",
            background=constants.LABEL_BG_COLOR,
            foreground="black",
        )

        # Configure styles - Frames
        style.configure(
            "TFrame",
            background=constants.FRAME_BG_COLOR,
        )

        # Configure styles - Option Menu
        style.configure(
            "TMenubutton",
            font=(None, constants.ELEMENT_FONT_SIZE),
            background=constants.FRAME_BG_COLOR,
            foreground="white",
        )

        return style
