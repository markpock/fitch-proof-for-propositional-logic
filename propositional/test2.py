from sentence import Sentence

a = Sentence('(P & Q) & (P v Q)')
print(a.tf.__str__(True))
print(repr(a.tf))