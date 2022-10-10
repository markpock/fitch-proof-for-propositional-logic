from proof import Proof

def human(proof: Proof):
    
    proof.append(other=proof[1].first)
    currline1 = proof.line
    
    proof.append('>E', [currline1, 2])
    endline1 = proof.line

    proof.append(other=proof[1].second, fl=False)
    currline2 = proof.line
    
    proof.append('>E', [currline2, 3])
    endline2 = proof.line

    proof.append('vE', [1, [currline1, endline1], [currline2, endline2]])


def main():
    print('Proof 1: Human')
    proof1 = Proof(['PvQ', 'P>R', 'Q>R'])
    human(proof1)
    print(proof1)

    print('Proof 2: Machine')
    proof2 = Proof(['PvQ', 'P>R', 'Q>R'])
    result_flag = proof2.prove('R')
    print(result_flag)
    print(proof2)


if __name__ == '__main__':
    main()