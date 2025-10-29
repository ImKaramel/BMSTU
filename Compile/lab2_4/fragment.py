from dataclasses import dataclass

from position import Position


@dataclass
class Fragment:
    starting: Position
    following: Position

    def __str__(self):
        return f"{self.starting}-{self.following}"