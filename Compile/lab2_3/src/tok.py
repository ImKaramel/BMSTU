import enum
from dataclasses import dataclass

from src.position import Fragment


class DomainTag(enum.Enum):
    AXIOM = "AXIOM"
    EPS = "EPS"
    KEY_OR = "KEY_OR"
    TERM = "TERM"
    NTERM = "NTERM"
    OP_ARROW = "OP_ARROW"
    KEY_END = "KEY_END"
    END_OF_PROGRAM = "END_OF_PROGRAM"
    ERROR = "ERROR"

    def __str__(self):
        return self.value


@dataclass
class Token:
    tag: DomainTag
    coords : Fragment
    val: str

    def __str__(self):
        return f"{self.tag} {str(self.coords.Starting), str(self.coords.Following)} : {self.val}"


