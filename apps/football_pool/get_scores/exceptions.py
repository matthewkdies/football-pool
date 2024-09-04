class NoESPNDataError(Exception):
    def __init__(self, url: str) -> None:
        super().__init__(f'No JSON data found when querying "{url=}".')
