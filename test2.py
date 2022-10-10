from sentence import Sentence

a = Sentence('~(R - (~S v T))')
print(a)
print(a.tf)

b = Sentence('(R & S & ~T) v (~R & ~S) v (~(R - S) & (S & T))')
print(b)
print(b.tf)

c = Sentence('(R & S & ~T) v (~R & ~S) v (~R & S & T)')
print(c)
print(c.tf)

d = Sentence('(R & S & ~T) v (~R & ~S) v (~R & T)')
print(d)
print(d.tf)

print(a.tf == b.tf)
print(a.tf == c.tf)
print(c.tf == b.tf)
print(d.tf == c.tf)