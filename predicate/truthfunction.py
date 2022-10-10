from copy import copy
from typing import Iterable


class TruthFunction:
    """
    Represents the TruthFunction of a Sentence. Supports printing, computation,
    and comparison - equality is measured in terms of the strength of the
    function. If a TruthFunction is greater than to or equal to another, 
    it is stronger - and thus the Sentence with said TruthFunction can
    prove the second sentence.
    """
    def __init__(self, sentence: 'Sentence'):
        """
        Creates a new TruthFunction on the given atomics for the given Sentence.
        """
        self.sentence = sentence
        self.atomics = sorted(set(char for char in sentence.formula if char.isupper()))
        self.true, self.false = [], []
        self.canonical = self._canonical(self.atomics)
        for vals in self.canonical:
            if self(vals):
                self.true.append(vals)
            else:
                self.false.append(vals)

    def _canonical(self, atomics: Iterable) -> list[dict[str, bool]]:
        """
        Generates the canonical form for given atomics - a list of dictionaries
        corresponding to every possible combination of truth values.
        """
        canonical = [{}] * 2 ** len(atomics)
        for i, vals in zip(range(2 ** len(atomics)), canonical):
            for j, atomic in zip(range(len(atomics)), atomics):
                if i // (2 ** (len(atomics) - j - 1)) % 2 == 0:
                    vals[atomic] = True
                else:
                    vals[atomic] = False
        return canonical

    def __len__(self) -> int:
        """
        Returns the length of the canonical form of the truth function.
        """
        return 2 ** len(self.atomics)
    
    def __call__(self, vals: dict[str, bool]) -> bool:
        """
        Computes the truth function of a particular assignment of values to
        the atomics of the sentence.
        """
        return self.sentence.root(vals)

    def __str__(self) -> str:
        """
        Returns a String representation of the TruthFunction in canonical form.
        """
        result, arr = f'{"  ".join(self.atomics)}\n', []
        for vals in self.canonical:
            arr.append(f'{"  ".join([str(val)[0] for val in vals.values()])}   {self(vals)}\n')
        return result + ''.join(arr)

    def __gt__(self, other: 'TruthFunction') -> bool:
        """
        Checks to see if this TruthFunction is strictly stronger than the other
        TruthFunction - if the Sentence from which the former is derived can
        prove the Sentence from which the other is derived and the Sentences
        are not logically equivalent.
        """
        if self == other:
            return False
        other_canon = self._canonical(set(other.atomics).difference(set(self.atomics)))
        curr_val = True
        for vals in self.true:
            vals: dict[str, bool] = copy(vals)
            for other_vals in other_canon:
                curr_val = curr_val and other(dict(vals, **other_vals))
            if not curr_val:
                return curr_val
        return curr_val

    def __ge__(self, other: 'TruthFunction') -> bool:
        """
        Checks to see if this Truth Function is weakly stronger than the other
        Truthfunction - i.e., its Sentence can prove the other Sentence.
        """
        return self == other or self > other

    def __eq__(self, other: 'TruthFunction') -> bool:
        """
        Checks to see if the TruthFunctions are logically equivalent. For
        proof purposes, takes into account the specific propositional
        variables used.
        """
        return str(self) == str(other)
    
    def taut(self, val: bool) -> bool:
        if val:
            result = True
            for vals in self.canonical:
                result = result and self(vals)
        else:
            result = False
            for vals in self.canonical:
                result = result or self(vals)
            result = not result
        return result
    
    def __repr__(self) -> str:
        return str(self)