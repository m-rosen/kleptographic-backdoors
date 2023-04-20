''' Implementation of the backdoor described in How to Backdoor LWE-like cryptosystems, using Elligator 1

Written by Miriam Rosén in 2023

This file contains an implementation of the backdoored seed generation
procedure described by Hemmert in the paper "How to Backdoor LWE-like cryptosystems".
This version of uses the mapping function Elligator 1.

Runs n retrieval tests, and writes m seed pairs to a binary file "out_hemmert_elli1.bin",
additionally writes the number of tries it took to find valid seeds to file "out_hemmert_elli1_tries.txt"
Default value of n is 100 and m is 10^3.
Approximate time to generate 10^3 seeds is 20 seconds.

Example use:

    python ./backdoor_hemmert_elli1.py

    python ./backdoor_hemmert_elli1.py [n] [m]

    python ./backdoor_hemmert_elli1.py [n] [m] [output dir]
        Note! dir must exist before running the program
'''


from ecpy.curves import Point, TwistedEdwardCurve
from elligator.elligator1 import Elligator1
import secrets
import time
import sys

# Setup =============================================================================
q = 2**257 - 93
d = 1088
s = 14697352851676074552963121469662559050531125212681422018744685276304061464803
elli = Elligator1(q, d, s)

# Found using generator.sage
p = 57896044618658097711785492504343953926456108821618088776478188676453023211901
_G_ed = [
    228372640616428539900130013049815066326154907798774733358185911637216892286314,
    165508619038704143113488945898290217115626586457192633182952257675369618343994
]
_domain = {
    "name" : "hemmert_curve",
    "type" : "TwistedEdward",
    "size" : 257,
    "a" : 1,
    "d" : 1088,
    "field" : 2**257 - 93,
    "generator" : _G_ed,
    "order" : 4*p
}
E = TwistedEdwardCurve(_domain)

Q = E.generator
R = Point(1, 0, E)
# ==================================================================================


def ecdh_key_pair():
    '''
    Generate an Elliptic Curve Diffie Hellman key pair.
    '''
    sk = secrets.randbelow(4*p)
    pk = sk * Q
    return (pk, sk)


def seed_gen(pk_a):
    '''
    Generate backdoored seeds.

    pk_a (Point): adversary public key (=yG)

    Returns: (public seed, private seed, nr_tries)
    '''
    tries = 0
    seed_pub = None
    seed_priv = None
    while True:
        tries +=1
        if tries > 100:
            print("Maximum number of tries reached")
            exit()

        b = secrets.randbelow(int(4*p))
        r = secrets.randbelow(4)

        im_pub = b*Q
        im_priv = r*R + b*pk_a

        # Try to compute the preimage
        if elli.in_image(im_pub.x, im_pub.y) and elli.in_image(im_priv.x, im_priv.y):
            seed_pub = elli.inv_map(im_pub.x, im_pub.y)
            seed_priv = elli.inv_map(im_priv.x, im_priv.y)
            break

    return seed_pub, seed_priv, tries


def seed_retrival(seed_pub, sk_a):
    '''
    Retrive the private seed from the public.
    
    seed_pub (Int)  : public seed
    sk_a     (Point): adversary secret key

    Returns : retrived private seed
    '''
    # Generate A from seed_pub
    u, v = elli.map(seed_pub)
    B = Point(u, v, E)
    C = sk_a * B
    valid = []
    for r in range(0, 4):
        sk = r*R + C
        if elli.in_image(sk.x, sk.y):
            # TODO: Generate s and e from seed_priv
            # If b == As + e mod q return seed_priv
            seed_priv = elli.inv_map(sk.x, sk.y)
            valid.append(seed_priv)

    return valid


def test_backdoor():
    '''
    Test the backdoor mechanism on curve: y^2 + x^2 = 1 + dx^2y^2 
    over finite field of size q.
    '''

    pk_a, sk_a = ecdh_key_pair()
    seed_pub, seed_priv, nr_tries = seed_gen(pk_a)
    print(f'Took {nr_tries} tries to find valid seeds')
    # TODO: Use seeds to generate actual key
    possible_seeds = seed_retrival(seed_pub, sk_a)

    print("Results")
    print("---------------------------")
    res = False
    for i, s in enumerate(possible_seeds):
        match = s == seed_priv
        res |= match
        print(f'Seed {i}: match: {match}, value: {s}')
    
    assert res, 'Seed retrival failed'


def test_backdoor(nr_tests):
    '''
    Test the backdoor mechanism on curve:  y^2 + x^2 = 1 + dx^2y^2
    over finite field of size q, multiple times.
    '''

    pk_a, sk_a = ecdh_key_pair()
    success = 0
    start = time.time()
    for i in range(0, nr_tests):
        seed_pub, seed_priv, nr_tries = seed_gen(pk_a)
        possible_seeds = seed_retrival(seed_pub, sk_a)
        res = False
        for i, s in enumerate(possible_seeds):
            match = s == seed_priv
            res |= match

        if (res):
            success += 1
    
    print(f"Successful tests: {success}/{nr_tests}")
    print(f"Time taken: {round(time.time() - start, 2)} s")


def collect_data(nr_tests, file):
    pk_a, sk_a = ecdh_key_pair()
    seed_file = open(f"{file}.bin", "wb")
    tries_file = open(f"{file}_tries.txt", "w")
    start = time.time()
    tries = 0
    for i in range(0, nr_tests):
        seed_pub, seed_priv, nr_tries = seed_gen(pk_a)
        seed_file.write(int(seed_pub).to_bytes(32, 'little'))
        seed_file.write(int(seed_priv).to_bytes(32, 'little'))
        tries_file.write(f"{nr_tries}\n")
        tries += nr_tries

    seed_file.close()
    tries_file.close()

    print(f"Wrote {nr_tests} seed pairs to file {file}")
    print(f"Took {round(tries / nr_tests, 3)} tries to find valid seeds on average. ")
    print(f"Time taken: {round(time.time() - start, 2)} s")


if __name__ == "__main__":
    nr_tests = 100
    nr_samples = 1000
    file = "out_hemmert_elli1"

    if len(sys.argv) >= 3:
        nr_tests = int(sys.argv[1])
        nr_samples = int(sys.argv[2])
    
    if len(sys.argv) >= 4:
        dir = sys.argv[3]
        file = dir + '/' + file

    if nr_tests > 0:
        test_backdoor(nr_tests)
    
    if nr_samples > 0:
        collect_data(nr_samples, file)