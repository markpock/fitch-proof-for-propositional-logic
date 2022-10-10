from truthfunction import TruthFunction
from sentence import Sentence

a = Sentence('(P & Q) & (P v Q)')
b = Sentence('(P & R) & (P v Q)')

print(TruthFunction.compare([a, b]))