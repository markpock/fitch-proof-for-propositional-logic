from truthfunction import TruthFunction
from sentence import Sentence

a = Sentence('P > (Q > R)')
b = Sentence('(P > Q) > R')
print(a.equivalent(b))
print(TruthFunction.compare([a, b, Sentence('(~P & ~Q) > ~R')]))