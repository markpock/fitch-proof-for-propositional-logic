from __future__ import annotations
from typing import Union


NULLARIES = ['#']
SPEC_NULLARIES = ['⊥']

UNARIES = ['~']
SPEC_UNARIES = ['¬']

BINARIES = ['v', '&', '^', '>', '-']
SPEC_BINARIES = [' ∨ ', ' ∧ ', ' ⊕ ', ' ⟶  ', ' ⟷  ']

CONNECTIVES = ['#', '~', 'v', '&', '^', '>', '-']
SPEC_CONNECTIVES = ['⊥', '¬', ' ∨ ', ' ∧ ', ' ⊕ ', ' ⟶  ', ' ⟷  ']

VALID = '()#~v&^>-⊥¬∨∧⊕⟶⟷ '

TFS = {'~': lambda p: not p,
       'v': lambda p, q: p or q,
       '&': lambda p, q: p and q,
       '>': lambda p, q: not p or q,
       '-': lambda p, q: TFS['>'](p, q) and TFS['>'](q, p), 
       '^': lambda p, q: not TFS['-'](p, q)}


class Symbol:
    """
    Represents a Symbol - either an atomic or connective - of the propositional
    calculus.
    """
    def __init__(self, symbol: str, left: Symbol = None, right: Symbol = None, formula: str = None):
        """
        Constructs a Symbol with the given attributes. Formula refers to the
        formula enclosed by the Symbol - information which is governed by the
        ParseTree as well, and does not have to be provided.
        """
        self.symb, self.left, self.right, self.formula = symbol, left, right, formula
        if symbol in BINARIES or symbol in UNARIES:
            self.type = 'connective'
        elif symbol in NULLARIES:
            self.type = 'constant'
        else:
            self.type = 'atomic'

    def __eq__(self, other: Union[Symbol, str]) -> bool:
        """
        Checks whether or not two Symbols store the same symbol.
        """
        if isinstance(other, Symbol):
            return self.symb == other.symb
        if isinstance(other, str):
            return self.symb == other
        raise TypeError()

    def __call__(self, vals: dict[str, bool]) -> bool:
        """
        Returns the truth function when given particular values for each of the
        propositional variables.
        """
        if self.symb == '#':
            return False
        if self.symb == '~':
            return TFS[self.symb](self.left(vals))
        if self.type == 'atomic':
            return vals[self.symb]
        return TFS[self.symb](self.left(vals), self.right(vals))

    def __hash__(self):
        return hash(self.formula)
