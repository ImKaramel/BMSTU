

from enum import Enum
class DomainTag(Enum):
    VARNAME = 0
    FUNCNAME = 1
    INT_CONST = 2
    CHAR_CONST = 3
    STRING_CONST = 4
    KEYWORD = 5
    SPEC_SYMB = 6
    ERR = 7
    EOP = 8


tagToString = {
    DomainTag.VARNAME: "VARNAME",
    DomainTag.FUNCNAME: "FUNCNAME",
    DomainTag.INT_CONST: "INT_CONST",
    DomainTag.CHAR_CONST: "CHAR_CONST",
    DomainTag.STRING_CONST: "STRING_CONST",
    DomainTag.KEYWORD: "KEYWORD",
    DomainTag.SPEC_SYMB: "SPEC_SYMB",
    DomainTag.EOP: "EOP",
    DomainTag.ERR: "ERR"
}

keywords = {
    "bool",
    "char",
    "int",
    "false",
    "true",
    "nothing",
    "new_",
    "not_"
}

keywordsWithUnderliningStart = {
    "_and_",
    "_eq_",
    "_ge_",
    "_gt_",
    "_le_",
    "_lt_",
    "_mod_",
    "_ne_",
    "_or_",
    "_pow_",
    "_xor_"
}

specSymbsInOneRune = {
    "<",
    ">",
    "(",
    ")",
    "[",
    "]",
    ",",
    "?",
    "&",
    "\\",
    "^",
    "-",
    "*",
    "/"
}
