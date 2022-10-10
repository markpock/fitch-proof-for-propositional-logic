from typing import Union
from sentence import Sentence
from basis import CONNECTIVES, SPEC_CONNECTIVES


class Rule:
    def __init__(self, name, arguments: list = None):
        """
        Constructs a new rule with the given name and arguments. Should not be
        used directly unless constructing a Premise or Assume - all other rules
        should be constructed using the factory method apply.
        """
        self.name, self.arguments = name, arguments

    def __str__(self) -> str:
        """
        Returns a string representation of the rule in Fitch proof style.
        """
        final = Sentence._replace(self.name[0], CONNECTIVES, [conn.strip() + ' ' for conn in SPEC_CONNECTIVES])
        final = f'{final}{self.name[1:]}'
        if self.arguments:
            final += '; ' + ', '.join([str(arg) for arg in self.arguments])
        return final

    @classmethod
    def apply(cls, rule: str, premises, lines: Union[list[int], int],
              other: Sentence = None, fl: bool = True) -> tuple['Rule', Union[Sentence,
              tuple[Sentence]], int, int]:
        """
        Applies the given rule to the premises indicated by lines. See the
        Proof.append documentation for the full excruciating details about rule,
        lines, other, fl, and how they interact. The return type is important to
        note here - the Rule is returned first, then the Sentence (or Sentences
        in the case of an &E), then the indentation level, then the access
        modifier.
        """
        from proof import Proof
        premises: Proof = premises
        if not fl and isinstance(lines, list):
            lines.reverse()
        indent = premises.indent
        match rule:
            case 'assume':
                indent = indent + int(fl)
                return cls('Assume'), other, indent, premises._get_access(indent)
            case 'reit':
                return cls('Reit', [lines]), premises[lines], indent, premises.access
            case '#E':
                return cls('#Elim', [lines]), other, indent, premises.access
            case '#I':
                return cls('#Intro', lines), Sentence('#'), indent, premises.access
            case '~E':
                return cls('~Elim', [lines]), premises[lines].first.first, indent, premises.access
            case '~I':
                args = [f'{str(min(lines))} - {str(max(lines))}']
                return cls('~Intro', args), premises[min(lines)].negate(), indent - 1, premises.access // 10
            case '&E':
                theorem = (premises[lines].first, premises[lines].second)
                return cls('&Elim', [lines]), theorem, indent, premises.access
            case '&I':
                theorem = premises[lines[0]].join(premises[lines[1]], '&')
                return cls('&Intro', sorted(lines)), theorem, indent, premises.access
            case 'vE':
                args = [arg for arg in lines if isinstance(arg, int)]
                args.extend(cls._section_order(lines, 1, 2))
                return cls('vElim', args), premises[lines[1][-1]], indent - 1, premises.access // 10
            case 'vI':
                rule = cls('vIntro', [lines])
                if not fl:
                    return rule, other.join(premises[lines], 'v'), indent, premises.access
                return rule, premises[lines].join(other, 'v'), indent, premises.access
            case '>E':
                if premises[lines[0]].mc == '>' and premises[lines[0]].first == premises[lines[1]]:
                    conditional = premises[lines[0]]
                else:
                    conditional = premises[lines[1]]
                return cls('>Elim', sorted(lines)), conditional.second, indent, premises.access
            case '>I':
                args = [f'{str(min(lines))} - {str[min(lines[-1])]}']
                theorem = premises[lines[0]].join(premises[lines[-1]], '>')
                return cls('>Intro', args), theorem, indent - 1, premises.access // 10
            case '-E':
                if premises[lines[0]].mc == '>':
                    conditional = premises[lines[0]]
                else:
                    conditional = premises[lines[1]]
                if conditional.first == premises[lines[0]]:
                    theorem = conditional.second
                else:
                    theorem = conditional.first
                return cls('-Elim', sorted(lines)), theorem, indent, premises.access
            case '-I':
                theorem = premises[lines[0][0]].join(premises[lines[0][-1]], '-')
                return cls('-Intro', cls._section_order(lines, 0, 1)), theorem, indent - 1, premises.access // 10

    @classmethod
    def _section_order(cls, lines: list, start: int, stop: int) -> list[str]:
        """
        Determines how a rule taking sections as arguments should look based
        on the ordering of the sections. Assumes the sections are themselves
        part of a list and takes the two relevant indices as parameters start
        and stop.
        """
        if lines[stop][start] < lines[start][start]:
            args = [f'{str(lines[stop][0])} - {str(lines[stop][-1])}', 
                    f'{str(lines[start][0])} - {str(lines[start][-1])}']
        else:
            args = [f'{str(lines[start][0])} - {str(lines[start][-1])}', 
                    f'{str(lines[stop][0])} - {str(lines[stop][-1])}']
        return args
    
    def __repr__(self) -> str:
        return str(self)
