"""
Calculates sum of all primes below given integer n
"""
import Library_IsPrime

#def sum_primes(n):
def Main(
    Integer,
    ):
    n = Integer
    return sum([x for x in range(2,n) if Library_IsPrime.Main(x)])

