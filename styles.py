class GameStyles:
    """Includes the style specifications of the AGV COntrol GUI"""

    FONT_SIZE = 20
    PADDING = 20

    @staticmethod
    def config_styles(style) -> None:
        style.configure(
            "TButton",
            background="#fcc200",
            font=(None, GameStyles.FONT_SIZE),
            padding=GameStyles.PADDING,
        )

        # Configure styles - Labels
        style.configure(
            "TLabel",
            font=(None, GameStyles.FONT_SIZE),
            # background="#5e0009",
            background="#fcc200",
            foreground="black",
            padding=GameStyles.PADDING,
        )

        # Configure styles - Frames
        style.configure(
            "TFrame",
            background="#5e0009",
        )
        return style
