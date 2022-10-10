from sentence import Sentence
from proof import Proof


def prove(conclusion: Sentence, proof: Proof, indent: int, flags: list) -> bool:
    if conclusion in [prior[0] for prior in proof.priors] and proof.indent == indent:
        return True
    # Work with conclusions
    match conclusion.mc:
        case '>':
            proof.append(other=conclusion.first)
            currline = proof.line
            if prove(conclusion.second, proof):
                proof.append('>I', [currline, proof.line])
                return True
            else:
                proof.pop()
                return False
    # Work with premises
    for theorem, line in proof.priors:
        match theorem.mc:
            case 'v':
                if ['pbc', theorem] in flags:
                    continue
                flags.append(['pbc', theorem])
                proof.append(other=theorem.first)
                disjunct1_start = proof.line
                if not prove(conclusion, proof, indent + 1, flags):
                    flags.pop()
                    proof.pop()
                    continue
                disjunct1_end = proof.line
                proof.append(other=theorem.second, fl=False)
                disjunct2_start = proof.line
                if not prove(conclusion, proof, indent + 1, flags):
                    flags.pop()
                    proof.pop()
                    while proof.indent == indent:
                        proof.pop()
                    continue
                disjunct2_end = proof.line
                proof.append('vE', [line, [disjunct1_start, disjunct1_end], [disjunct2_start, disjunct2_end]])
                flags.pop()
                if prove(conclusion, proof, indent, flags):
                    return True
                continue
            case '>':
                for antecedent, ant_line in proof.priors:
                    if antecedent == theorem.first and theorem.second not in proof.priors:
                        proof.append('>E', [ant_line, line])
                        if prove(conclusion, proof, indent, flags):
                            return True
                        continue
    return False




def main():
    proof = Proof(['PvQ', 'P>R', 'Q>R'])
    sent = 'R'
    conclusion = Sentence(sent)