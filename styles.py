import constants


class GameStyles:
    """Includes the style specifications of the GUI"""

    @staticmethod
    def config_styles(style) -> None:
        style.configure(
            "TButton",
            background=constants.LABEL_BG_COLOR,
            font=(None, constants.ELEMENT_FONT_SIZE),
            padding=constants.ELEMENT_PADDING,
        )

        # Configure styles - Labels
        style.configure(
            "TLabel",
            font=(None, constants.ELEMENT_FONT_SIZE),
            background=constants.LABEL_BG_COLOR,
            foreground="black",
            padding=constants.ELEMENT_PADDING,
        )

        # Configure styles - Frames
        style.configure(
            "TFrame",
            background=constants.FRAME_BG_COLOR,
        )

        return style
