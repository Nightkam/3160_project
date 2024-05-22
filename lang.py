from typing import Any, Dict, Tuple, Union, Optional

Parser = Union[Tuple[Any, int], None]

class Expression:
    def __init__(self, l: 'Fact', op: str, r: 'Fact'):
        self.l = l
        self.op = op
        self.r = r

class Fact:
    def __init__(self, unary: Optional[str] = None, exp: Optional['Fact'] = None, value: Union[int, str, 'Expression', None] = None):
        self.unary = unary
        self.exp = exp
        self.value = value

def parse_ident(text: str) -> Optional[Tuple[str, int]]:
    import re
    ident_reg = re.match(r'^[a-zA-Z_][a-zA-Z_0-9]*', text)
    if not ident_reg:
        return None
    ident = ident_reg.group(0)
    return ident, len(ident)

def parse_assignment(text: str) -> Optional[Tuple[Tuple[str, Fact], int]]:
    length = 0

    def t() -> str:
        return text[length:]

    ident = parse_ident(text)
    if not ident:
        return None
    identifier, ident_length = ident
    length += ident_length

    if not t().startswith(' = '):
        return None
    length += 3

    exp = parse_exp(t())
    if exp:
        value, exp_length = exp
        length += exp_length
    else:
        fact = parse_fact(t())
        if not fact:
            return None
        value, fact_length = fact
        length += fact_length

    if not t().startswith(';'):
        return None
    length += 1
    return (identifier, value), length

def parse_exp(text: str) -> Optional[Tuple[Expression, int]]:
    length = 0
    values = []

    def t() -> str:
        return text[length:]

    a = parse_fact(t())
    if not a:
        return None
    a_val, a_length = a
    values.append(a_val)
    length += a_length

    import re
    op_reg = re.match(r'^[*+-]', t())
    if not op_reg:
        return None
    op = op_reg.group(0)
    values.append(op)
    length += len(op)

    b = parse_fact(t())
    if not b:
        return None
    b_val, b_length = b
    values.append(b_val)
    length += b_length

    val = Expression(a_val, op, b_val)
    return val, length

def parse_fact(text: str) -> Optional[Tuple[Fact, int]]:
    import re

    exp_reg = re.match(r'^\((.+?)\)', text)
    if exp_reg:
        parsed = parse_exp(exp_reg.group(1))
        if not parsed:
            return None
        parsed_val, parsed_length = parsed
        return Fact(value=parsed_val), parsed_length + 2

    if text[0] in "-+":
        parsed = parse_fact(text[1:])
        if not parsed:
            return None
        parsed_val, parsed_length = parsed
        return Fact(unary=text[0], exp=parsed_val), parsed_length + 1

    lit_reg = re.match(r'^0|[1-9]\d*', text)
    if lit_reg:
        val = int(lit_reg.group(0))
        return Fact(value=val), len(lit_reg.group(0))

    ident_reg = re.match(r'^[a-zA-Z_][a-zA-Z_0-9]*', text)
    if ident_reg:
        ident = ident_reg.group(0)
        return Fact(value=ident), len(ident)

def resolve_fact(variables: Dict[str, int], fact: Fact) -> int:
    if isinstance(fact.value, int):
        return fact.value
    if isinstance(fact.value, str):
        return variables[fact.value]
    if fact.unary:
        if fact.unary == '-':
            return -resolve_fact(variables, fact.exp)
        return resolve_fact(variables, fact.exp)
    if isinstance(fact.value, Expression):
        left = resolve_fact(variables, fact.value.l)
        right = resolve_fact(variables, fact.value.r)
        if fact.value.op == '-':
            return left - right
        if fact.value.op == '+':
            return left + right
        if fact.value.op == '*':
            return left * right
    raise ValueError('impossible state reached')


program = """
x = 1;
y = 2;
z = ---(x+y)*(x+-y);
""".strip()

variables: Dict[str, int] = {}
for line in program.split("\n"):
    parsed = parse_assignment(line)
    if not parsed:
        print("error")
        exit(1)
    identifier, value = parsed[0]

    if isinstance(value, Expression):
        value = Fact(None, None, value)
    variables[identifier] = resolve_fact(variables, value)

for key, val in variables.items():
    print(f"{key} = {val}")
