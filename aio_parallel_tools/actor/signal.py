"""Sigals to send to actors."""


class ActorExit(Exception):
    """Tell Actor it's time to close."""

    pass
