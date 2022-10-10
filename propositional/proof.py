from __future__ import annotations
from copy import copy
from rule import Rule
from sentence import Sentence
from typing import Generator, Iterable, Union

class Proof:
    """
    Represents the entirety of a Proof. Only makes distinctions between nine
    same-level assumptions at a time.
    """
    def __init__(self, premises: Iterable[Union[str, Sentence]]):
        """
        Creates a new Proof from the given premises with indents everywhere.
        """
        premises = copy(premises)
        for i, premise in zip(range(len(premises)), premises):
            if isinstance(premise, str):
                premises[i] = Sentence(premise)
        self.theorems: list[Sentence] = list(premises)
        self.premises: list[Sentence] = copy(self.theorems)
        self.rules = [Rule('Premise') for _ in premises]
        self.indents = [0 for _ in premises]
        self.accesses = [1 for _ in premises]

    def __str__(self) -> str:
        """
        Returns the Proof as a str in Fitch proof style.
        """
        if len(self) == 0:
            return 'Proof:'
        if len(self.premises) > 0:
            opener = f'\n{", ".join(str(p) for p in self.premises)}'
        else:
            opener = '∅'
        opener += f' ⊢ {str(self.theorems[-1])}\nProof:\n'
        result = []
        ilen = len(str(max(self.index))) + 2
        tlen = max([len(theorem) for theorem in self.theorems]) + 20
        for i in self.index:
            index = str(i) + ' ' * (ilen - len(str(i)))
            index += '|  ' * self.indents[i - 1]
            theorem = str(self[i]) + ' ' * (tlen - len(str(self[i])) - 3 * self.indents[i - 1])
            result.append(f'{index}{theorem}{str(self.rules[i - 1])}\n')
        return opener + ''.join(result) + ' ' * (ilen + tlen) + '∎.\n\n'

    def __len__(self) -> int:
        """
        Returns the number of lines in the Proof.
        """
        return len(self.theorems)

    def __getitem__(self, line: int) -> Sentence:
        """
        Gets the theorem at the given line as a Sentence. Slices are inclusive.
        """
        if isinstance(line, slice):
            return self.theorems[line.start - 1: line.stop]
        if isinstance(line, int):
            return self.theorems[line - 1]
        
    def __iter__(self) -> Generator:
        """
        Returns a Generator to iterate over the proof, line by line.
        """
        for i in self.index:
            yield self[i]

    def append_sentence(self, indent: int, theorem: Union[Sentence, str], rule: Rule = Rule('Assume'), access: int = None):
        """
        Appends a new Sentence to the Proof. If the rule is not given, defaults
        to 'Assume.'
        """
        if isinstance(theorem, str):
            theorem = Sentence(theorem)
        if not access:
            if rule == Rule('Assume') or indent > self.indent:
                self.accesses.append(self._get_access(indent))
            elif indent == self.indent:
                self.accesses.append(self.access)
            elif indent < self.indent:
                self.accesses.append(self.access // 10)
        else:
            self.accesses.append(access)
        self.indents.append(indent)
        self.theorems.append(theorem)
        self.rules.append(rule)

    def pop(self):
        """
        Removes the previously added line.
        """
        self.indents.pop()
        self.theorems.pop()
        self.rules.pop()
        self.accesses.pop()

    def append(self, rule: str = 'assume', lines: Union[list[int], int] = None,
              other: Union[str, Sentence] = None, fl: bool = True):
        """
        Applies the given rule to the indicated lines and appends the result. Lines
        can be a list for rules that take multiple arguments or an int for rules that
        only take one. If a rule takes arguments other than those in the premises
        (e.g. #Elim and vIntro), those should be provided to other as a Sentence.
        Returns the resultant Rule and Sentence as a tuple. The symbols are here
        referred to as # (⊥), ~ (¬), & (∧), v (∨), > (⟶), and - (⟷),
        with rules indicated by I and E following the name of the symbol concerned.
        Reit is also here as 'reit.' Does not include DeM or BDC and does no
        validity checking when applying rules. Uses fl to determine ordering.
        If fl is true (the default), will put the connective which comes first
        in the provided lines on the left and the others afterwards. Also uses
        fl for &E - if fl is True (the default) will take the left argument,
        and the right argument if fl is False. Squeezes fl for all it's worth -
        fl = False is also used to indicate a same-level assumption such as in
        vE.

        # Arguments for rules:
        - Provide the line number to Reit as an integer to lines.
        - Provide the Sentence desired as a result for #E as a Sentence to other,
          providing the line number of the contradiction to lines.
        - Provide the line numbers to lines as a list for #I.
        - Provide the line number to ~E as an int.
        - Provide the line numbers to ~I as a list containing the first and last line
          in that order (so a slice of the proof index is also acceptable).
        - Provide the line number to &E as an int. By default, andoption takes the
          first argument, so be sure this is verified.
        - Provide the line numbers to &I as a list containing the two numbers as ints.
        - Provide a list like [3, [4, 5], [6, 7]] to vE.
        - Provide the line number to vI and a Sentence to the other parameter to
          disjoin it with.
        - Provide a list of ints to >E. >E will check which is the conditional.
        - Provide a list of ints (or slice) to >I.
        - Provide a list of ints to biE. BiE will check which is the conditional and
          which argument is to be inferred.
        - Provide a list of lists of int to biI like [[4, 5], [6, 7]].
        """
        if isinstance(other, str):
            other = Sentence(other)
        rule, new, indent, access = Rule.apply(rule, self, lines, other, fl)
        if isinstance(new, tuple):
            new = new[int(not fl)]
        self.append_sentence(indent, new, rule, access)
    
    def _get_access(self, indent: int) -> int:
        """
        Returns the access modifier associated with appending a Sentence to
        the Proof at the given level indent as an Assume (not under any
        other rule). Note that this indent is the level the Assume begins,
        not the level the Assume is appended from.
        """
        if indent not in self.indents:
            return 10 * self.access + 1
        curr_level_access = max([access for access in self.accesses if len(str(access)) == indent + 1])
        return curr_level_access + 1

    def accessible(self, accessee: int) -> Generator[tuple[Sentence, int]]:
        """
        Returns a Generator of the sentences a line number has access to.
        Particularly relevant when dealing with premise manipulation.
        The accessee is mostly treated as if it exists, and references its
        current position.
        """
        for i in self.index:
            if self._can_access(accessee, i):
                yield self[i], i
            else:
                continue
    
    def _can_access(self, accessee: int, accessed: int) -> bool:
        """
        Returns whether or not a certain line number has access to
        another line number as a theorem.
        """
        if accessee == len(self) + 1:
            accessee -= 1
        return str(self.accesses[accessee - 1]).startswith(str(self.accesses[accessed - 1]))
    
    def prove(self, conclusion: Union[Sentence, str]) -> str:
        from prove import prove
        """
        Attempts to prove the conclusion and write the necessary steps
        to the proof. If it can, returns True. If it cannot, returns
        False.
        """
        if isinstance(conclusion, str):
            conclusion = Sentence(conclusion)
        if len(self.premises) == 0:
            if not conclusion.tf.taut(True):
                return 'Not provable.'
        if Sentence.connect(self.premises, '&').tf < conclusion.tf:
            return 'Not provable from given premises.'
        if prove(conclusion, self, 0, []):
            return 'Proved.'
        else:
            return 'Failed to prove.'

    @property
    def index(self) -> Generator[int]:
        """
        Returns a Generator with the index of the Proof - each index will correspond
        to a line of the proof.
        """
        return range(1, len(self.theorems) + 1)
    
    @property
    def indent(self) -> int:
        """
        Returns the current level of indentation.
        """
        if len(self) == 0:
            return 0
        return self.indents[-1]
    
    @property
    def line(self) -> int:
        """
        Returns the line number of the most recently written to line.
        """
        return len(self)
    
    @property
    def access(self):
        """
        Returns the access modifier associated with the most recently written to
        line.
        """
        if len(self.accesses) == 0:
            return 1
        return self.accesses[-1]
    
    @property
    def priors(self) -> Generator[tuple[Sentence, int]]:
        """
        Returns the Sentences which the current line has access to - all the valid
        theorems of the language that follow from the current set of assumptions.
        """
        return self.accessible(self.line)
