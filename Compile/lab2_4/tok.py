from fragment import Fragment


from dataclasses import dataclass

from position import Position
from tag import DomainTag, tagToString

@dataclass
class Token:
    tag: DomainTag or None
    coord : Fragment or None
    val: str or None

    def __str__(self):
        return f"{tagToString[self.tag]} {str(self.coord.starting), str(self.coord.following)} : {self.val}"

    def Tag(self):
        return self.tag




# class Token:
#     def __init__(self, tag, starting, following, val):
#         self.tag = tag
#         self.coords = Fragment(starting, following)
#         self.val = val
#
#     def __str__(self):
#         return f"{tagToString[self.tag]} {self.coords}: {self.val}"
#
#     def Tag(self):
#         return self.tag


# @dataclass
# class Token:
#     tag: DomainTag
#     coords: Fragment
#     val: str
#
#     def __str__(self):
#         return f"{tagToString[self.tag]} {self.coords}: {self.val}"
#
#     def tag(self):
#         return self.tag