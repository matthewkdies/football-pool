class NoESPNDataError(Exception):
    """An exception for when ESPN doesn't return JSON data."""

    def __init__(self, url: str) -> None:
        super().__init__(f'No JSON data found when querying "{url=}".')


class GameNotOverError(ValueError):
    """An exception raised if a winner is computed for a Game that hasn't ended."""

    def __init__(self) -> None:
        super().__init__("Cannot compute a winner for a game that hasn't completed.")


class GameTiedError(ValueError):
    """An exception raised if a winner is computed for a Game that ended in a tie."""

    def __init__(self) -> None:
        super().__init__("Cannot compute a winner for a tied game.")
