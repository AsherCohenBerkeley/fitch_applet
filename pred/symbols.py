zeroary = [
    r'\bot'
]

unary = [
    r'\neg'
]

binary = [
    r'\wedge',
    r'\vee',
    r'\to',
    r'\leftrightarrow',
]

quants = [
    r"\forall",
    r"\exists"
]

identity = [
    '='
]

class LogicError(Exception):
    pass