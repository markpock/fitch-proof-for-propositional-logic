from io import TextIOWrapper
from typing import Generator, Union
from basis import SPEC_CONNECTIVES, CONNECTIVES, BINARIES, Symbol
from truthfunction import TruthFunction


class Sentence:
    def __init__(self, formula: str = None, root: Symbol = None):
        """
        Constructs a new sentence from either the formula or root. If both are
        provided, takes at face value (doesn't check for correspondence). If
        the formula alone is provided, will transform into a parsetree. If the
        root alone is provided, will get the formula from the root. Note:
        Empty sentences are not allowed.
        """
        if root:
            self.root = root
        else:
            formula = self._replace(formula, ['[', ']'], ['(', ')'])
            formula = self._replace(formula, SPEC_CONNECTIVES, CONNECTIVES)
            self.root = self._parse(formula.replace(' ', ''))
        self.formula = self.root.formula
        self.tf = TruthFunction(self)
        self.left, self.right = None, None
        if self.root.left:
            self.left = self.__class__(self.root.left.formula, self.root.left)
            if self.root.symb == '~':
                self.right = self.left
            else:
                self.right = self.__class__(self.root.right.formula, self.root.right)

    def _parse(self, formula: str) -> Symbol:
        """
        Parses a formula of the propositional calculus recursively and returns
        the Symbol corresponding to its main connectives - or atomic, if the
        formula is an atomic sentence.
        """
        start = self._setup(formula)
        if isinstance(start, Symbol):
            return start
        
        enclosed, connectives = self._enclosed(formula, start)
        if isinstance(enclosed, Symbol):
            return enclosed

        while start == 0 and enclosed:
            formula = formula[1:-1]
            start = self._setup(formula)
            if isinstance(start, Symbol):
                return start
            enclosed, connectives = self._enclosed(formula, start)
            if isinstance(enclosed, Symbol):
                return enclosed

        formula, mc_pos = self._same_scope(formula, connectives)
        mc = formula[mc_pos]
        arg1 = self._parse(self._trim(formula[:mc_pos]))
        arg2 = self._parse(self._trim(formula[mc_pos + 1:]))
        arg1_f = self._untrim(arg1.formula)
        arg2_f = self._untrim(arg2.formula) if arg2.symb != mc else arg2.formula
            

        return Symbol(mc, arg1, arg2, formula=f'{arg1_f}{mc}{arg2_f}')

    def _enclosed(self, formula: str, start: int) -> tuple[Union[bool, Symbol], Union[dict, None]]:
        """
        Establishes whether or not the formula is 'enclosed' - either fully
        enclosed by unnecessary parens which can dropped or the argument of
        a wide scope negation. Special note for behaviour - if the formula
        is a wide-scope negation, will start the next round of parsing
        and return the relevant negation Symbol.
        """
        group_depth, connectives, enclosed = 0, {}, True
        for index, char in zip(range(start, len(formula)), formula[start:]):
            if char == '(':
                group_depth +=1
            if char == ')':
                group_depth -= 1
            if group_depth == 0 and index != len(formula) - 1 and char in BINARIES:
                connectives[index] = char
                enclosed = False
        if start == 1 and enclosed:
            neg = self._parse(formula[1:])
            formula = neg.formula
            if len(formula) > 1:
                formula = f'({formula})'
            return Symbol('~', neg, neg, f'~{formula}'), None
        return enclosed, connectives

    def _setup(self, formula: str) -> Union[Symbol, int]:
        """
        Sets up the base case for the parse recursion - will return a Symbol
        corresponding to the atomic on an atomic if the formula is an
        atomic, similarly to enclosed. If not an atomic, sets a flag start
        as an int determining whether or not the formula begins as a negation.
        """
        if len(formula) == 1:
            return Symbol(formula, formula=formula)
        return int(formula[0] == '~')

    def _trim(self, arg: str) -> str:
        """
        Trims atomic arguments - removes the parentheses around them and
        returns the resultant str.
        """
        if len(arg) == 3 or len(arg) == 4:
            if arg[0] == '(' and arg[-1] == ')':
                arg = arg[1:-1]
        return arg

    def _untrim(self, arg: str) -> str:
        """
        Ensures that arguments are enclosed in parentheses if necessary,
        returning the resultant str.
        """
        if (arg[0] != '~' and len(arg) > 2) or (not self._enclosed(arg, 0)[0]):
            return f'({arg})'
        return arg

    def _same_scope(self, formula: str, connectives: dict[int, str]) -> tuple[str, int]:
        """
        Deals with connectives of the same scope, returning the rearranged
        formula. Tries to divide connectives evenly into two groups, and will
        make the second group larger if the number of connectives is odd.
        Returns the adjusted formula and the position of the main connectives.
        """
        connindex = sorted(connectives.keys())
        mc_pos = connindex[0]
        if len(connectives) > 1:
            num_args = len(connectives) + 1
            num_first_args = num_args // 2
            arg1_pos = connindex[num_first_args - 1]
            arg1 = formula[:arg1_pos]
            if num_first_args > 1:
                arg1 = f'({arg1})'
            formula = f'{arg1}{connectives[arg1_pos]}({formula[arg1_pos + 1:]})'
            mc_pos = len(arg1)
        return formula, mc_pos

    def __eq__(self, other: 'Sentence') -> bool:
        """
        Checks if two Sentences store precisely the same formulae. Does not
        account for orientation (thus PvQ != QvP).
        """
        return str(self) == str(other)

    def _equal(self, curr: Symbol, other: Symbol) -> bool:
        """
        Recursive check for equality, helper method for dunder equals.
        """
        if not other:
            return False
        this_eq = curr == other
        if curr.left:
            left_eq = self._equal(curr.left, other.left) or self._equal(curr.left, other.right)
            right_eq = self._equal(curr.right, other.right) or self._equal(curr.right, other.left)
            return this_eq and left_eq and right_eq
        if other.left:
            return False
        return this_eq

    def __str__(self) -> str:
        """
        Returns a string representation of the sentence.
        """
        return self._replace(self.formula, CONNECTIVES, SPEC_CONNECTIVES)
    
    def __len__(self) -> int:
        """
        Returns the length of the formula.
        """
        return len(self.formula)

    def __iter__(self) -> Generator:
        """
        Returns each unique subsentence (and the sentence itself) of the
        Sentence. Relevant for membership queries.
        """
        for val in self._generate(self):
            yield val

    def _iterate(self, curr: 'Sentence') -> Generator:
        """
        Recursively creates Generators for subtrees, acting as a Generator
        for the entire tree.
        """
        yield curr
        for val in self._generate(curr.first):
            yield val
        if not (curr.first is curr.second):
            for val in self._generate(curr.second):
                yield val
    
    def _yield(self, gen: Generator) -> Generator:
        """
        Ensures that there is no repetition in values yielded from an
        _iterate generate - _iterate should always be closed in a
        _yield. Also catches StopIteration exceptions resulting from
        the close of a loop.
        """
        processed = set()
        val = next(gen)
        while not isinstance(val, Generator) and not (val is None):
            oldsize = len(processed)
            processed.add(val)
            if len(processed) > oldsize:
                yield val
            try:
                val = next(gen)
            except StopIteration:
                break
    
    def _generate(self, curr: 'Sentence') -> Generator:
        """
        Wraps _iterate in _yield. Should always be used.
        """
        return self._yield(self._iterate(curr))
    
    def __hash__(self):
        """
        Hashes this Sentence.
        """
        return hash(self.root) + hash(self.first) + hash(self.second)

    def is_negation(self, other: 'Sentence'):
        """
        Checks if this sentence is a negation of the other.
        """
        if self.root == '~':
            return self.first == other
        if other.root == '~':
            return self == other.first
        return False

    def negate(self):
        """
        Used to negate a sentence.
        """
        if self.root.symb == '~':
            return self.first
        formula = f'~{self._untrim(self.formula)}'
        return Sentence(formula, Symbol('~', self.root, self.root, formula))
    
    def join(self, other: 'Sentence', connective: str):
        """
        Used to join two sentences by a binary connective.
        """
        if other == None:
            return self
        formula = f'{self._untrim(self.formula)}{connective}{self._untrim(other.formula)}'
        return Sentence(formula, Symbol(connective, self.root, other.root, formula))
    
    def to_graph(self, filename: str = 'visualise'):
        Sentence.graph([self], filename)
    
    def deep_equal(self, other: 'Sentence') -> bool:
        """
        Checks if the two Sentences store the same formulae. Attempts to check
        for equality even when ordering differs (thus PvQ = QvP).
        """
        if other is None:
            return False
        return self._equal(self.root, other.root)
    
    def equivalent(self, other: 'Sentence') -> bool:
        """
        Does an equivalence check using truth functions.
        """
        return self.tf == other.tf

    @property
    def first(self) -> 'Sentence':
        """
        Returns the left subtree as a new Sentence.
        """
        return self.left

    @property
    def second(self) -> 'Sentence':
        """
        Returns the right subtree as a new Sentence.
        """
        return self.right
    
    @property
    def mc(self) -> str:
        """
        Returns the main connective of the Sentence as a str.
        """
        return self.root.symb

    @staticmethod
    def graph(sentences: list['Sentence'], filename: str = 'visualise'):
        """
        Represents the sentences in the given list visually in a GraphViz .gv
        file making use of the parsetree structure. Will be written to filename.gv.
        """
        with open(f'{filename}.gv', mode='w') as f:
            f.write('digraph {\n\n')
            for i, sentence in zip(range(len(sentences)), sentences):
                f.write(f'\tsubgraph s{i}' + ' {\n')
                f.write(f'\t\ts{i} [label = "{sentence.formula}"]\n')
                f.write(f'\t\ts{i} -> s{i}t\n')
                sentence._graph(sentence.root, f, f's{i}t')
                f.write('\t}\n\n')
            f.write('}\n')

    def _graph(self, curr: Symbol, f: TextIOWrapper, id:str):
        """
        Writes the contents of a Symbol to a .gv file and recurses to the linked
        Symbols.
        """
        f.write(f'\t\t{id} [label = "{curr.symb}"]\n')
        if not curr.left:
            return
        f.write(f'\t\t{id} -> ')
        if curr.left is curr.right:
            f.write(f'{id}n\n')
            self._graph(curr.left, f, f'{id}n')
        else:
            f.write(f'{id}l, {id}r\n')
            self._graph(curr.left, f, f'{id}l')
            self._graph(curr.right, f, f'{id}r')
    
    @staticmethod
    def _replace(arg: str, old: list[str], new: list[str]) -> str:
        """
        Replaces all occurrences of any substring contained in the list old with
        its corresponding string in the list new. Largely used to replace connectives
        with special characters where necessary.
        """
        for oldsub, newsub in zip(old, new):
            arg = arg.replace(oldsub, newsub)
        return arg
    
    def __repr__(self) -> str:
        return str(self)
    
    @staticmethod
    def connect(sentences: list['Sentence'], connective: str) -> 'Sentence':
        """
        Connects the sentences in the given list by the given connective, returning the
        result. Assumes there are one or more sentences in the list. Uses the grouping
        schema of attempting to balance at each level and favoring the second argument
        in size.
        """
        if len(sentences) == 0:
            return None
        if len(sentences) == 1:
            return sentences[0]
        num_args = len(sentences) // 2
        first = Sentence.connect(sentences[:num_args], connective)
        second = Sentence.connect(sentences[num_args:], connective)
        return first.join(second, connective)