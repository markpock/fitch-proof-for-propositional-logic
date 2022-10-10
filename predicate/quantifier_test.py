from sentence import Sentence


improper = 'A(PvQ)'
sent = Sentence(improper)
print(sent)

proper = 'Ax(PxvQx)'
sent = Sentence(proper)
print(sent)