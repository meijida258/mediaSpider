import timeit

def s(seq, i=0):
    if i == len(seq): return 0
    return s(seq, i+1) + seq[i]

print(s([1,2,3,4,5]))