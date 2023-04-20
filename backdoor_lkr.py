''' Implementation of the backdoor described in Lattice Klepto Revisited

Written by Miriam Rosén 2023

This file contains an implementation of the backdoored seed generation
procedure described in the paper "Lattice Klepto Revisited".

Runs n retrieval tests, and writes m seed pairs to a binary file "out_lkr.bin".
Default value of n is 100 and m is 10^3.
Approximate time to generate 10^3 seeds is 6 seconds.

Example use:

    python ./backdoor_lkr.py

    python ./backdoor_lkr.py [n] [m]

    python ./backdoor_lkr.py [n] [m] [output dir]
        Note! dir must exist before running the program
'''


from ecpy.curves import Curve, Point
import secrets
import time
import sys


def ecdh_key_pair(C : Curve, q : int, G : Point) -> tuple[Point, int]:
    '''
    Generate an Elliptic Curve Diffie Hellman key pair.

    Returns: (public key, private key)
    '''
    sk = secrets.randbelow(q)
    pk = C.mul_point(sk, G)
    return (pk, sk)


def seed_gen(C : Curve, q : int, G : Point, pk_a : Point) -> tuple[int, int]:
    '''
    Generate backdoored seeds.

    Returns: (public seed, private seed)
    '''
    pk, sk = ecdh_key_pair(C, q, G)
    ss = C.mul_point(sk, pk_a)

    seed_pub = pk.x
    seed_priv = ss.x

    return seed_pub, seed_priv


def seed_retrieval(C : Curve, seed_pub : int, sk_a : int):
    '''
    Retrieve the private seed from the public, procedure from LKR paper.
    '''
    # compute points P1_0, P1_1 whose x-coordinate is seed_pub
    y0 = C.y_recover(seed_pub, 0)
    y1 = C.y_recover(seed_pub, 1)

    P1_0 = Point(seed_pub, y0, C)
    P1_1 = Point(seed_pub, y1, C)

    # Compute P2_0 = sk_a*P1_0, P2_1 = sk_a*P1_1
    P2_0 = C.mul_point(sk_a, P1_0)
    P2_1 = C.mul_point(sk_a, P1_1)

    if P2_0.x == P2_1.x:
        return P2_0.x
    else:
        # TODO: Rerun key generaton and compare which choice
        # of seed leads to the correct complete public key
        return (P2_0.x, P2_1.x)


def seed_retrieval_simple(C : Curve, seed_pub : int, sk_a : int) -> int:
    '''
    Retrieve the private seed from the public, simplified procedure.
    '''
    # compute point whose x-coordinate is seed_pub
    y = C.y_recover(seed_pub, 0)
    P1 = Point(seed_pub, y, C)

    # Compute P2 = sk_a*P1
    P2 = C.mul_point(sk_a, P1)

    return P2.x


def test_retrieval_verbose(C : Curve, q : int, G : Point):
    # Adversary key gen
    pk_a, sk_a = ecdh_key_pair(C, q, G)
    print("adversary key pair:")
    print(f"    {pk_a}")
    print(f"    {sk_a}")

    seed_pub, seed_priv = seed_gen(C, q, G, pk_a)
    print("seeds:")
    print(f"    {seed_pub}")
    print(f"    {seed_priv}")

    recovered = seed_retrieval_simple(C, seed_pub, sk_a)
    print(f"recovered seed:")
    print(f"    {recovered}")

    if recovered == seed_priv:
        print("Successfully retrived private seed")


def test_retrieval(C : Curve, q : int, G : Point, nr_tests : int):
    # We will use curve y^2 = x^3 + 7 (secp256k1) over prime order field Fq
    # as described in Lattice Klepto Revisited
    C = Curve.get_curve("secp256k1")
    q = 2**256 - 2**32 - 977
    G = C.generator

    # Adversary key gen
    pk_a, sk_a = ecdh_key_pair(C, q, G)
    
    nr_success = 0
    start = time.time()
    for i in range(0, nr_tests):
        seed_pub, seed_priv = seed_gen(C, q, G, pk_a)
        recovered = seed_retrieval_simple(C, seed_pub, sk_a)

        if recovered == seed_priv:
            nr_success += 1
    
    print(f"Successful tests: {nr_success}/{nr_tests}")
    print(f"Time taken: {round(time.time() - start, 2)} s")


def collect_data(C : Curve, q : int, G : Point, n : int, file : str):
    # Adversary key gen
    pk_a, sk_a = ecdh_key_pair(C, q, G)

    start = time.time()
    fd = open(file, "wb")
    for i in range(0, n):
        seed_pub, seed_priv = seed_gen(C, q, G, pk_a)
        fd.write(seed_pub.to_bytes(32, 'little'))
        fd.write(seed_priv.to_bytes(32, 'little'))

    fd.close()
    print(f"Wrote {n} seed pairs to file {file}")
    print(f"Time taken: {round(time.time() - start, 2)} s")


if __name__ == "__main__":
    nr_tests = 100
    nr_samples = 1000
    file = "out_lkr.bin"

    if len(sys.argv) >= 3:
        nr_tests = int(sys.argv[1])
        nr_samples = int(sys.argv[2])
    
    if len(sys.argv) >= 4:
        dir = sys.argv[3]
        file = dir + '/' + file

    # We will use curve y^2 = x^3 + 7 (secp256k1) over prime order field Fq
    # as described in Lattice Klepto Revisited
    C = Curve.get_curve("secp256k1")
    q = 2**256 - 2**32 - 977
    G = C.generator

    if nr_tests > 0:
        test_retrieval(C, q, G, nr_tests)
    
    if nr_samples > 0:
        collect_data(C, q, G, nr_samples, file)
