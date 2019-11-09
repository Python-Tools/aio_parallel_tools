"""Exceptions and warnings."""


class ActorTimeoutWarning(Warning):
    """Actor Timeout Warning."""

    pass


class InboxNearllyFullWarning(Warning):
    """Inbox Nearlly Full Warning."""

    pass


class ActorIsPaused(Exception):
    """Actor is Paused."""

    pass


class NoAvailableActor(Exception):
    """No Available Actor."""
    
    pass
