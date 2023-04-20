''' Implementation of the backdoor described in How to Backdoor LWE-like cryptosystems, using Elligator 2

Written by Miriam Rosén in 2023

This file contains an implementation of the backdoored seed generation
procedure described by Hemmert in the paper "How to Backdoor LWE-like cryptosystems".
This version of uses the mapping function Elligator 2.

Runs n retrieval tests, and writes m seed pairs to a binary file "out_hemmert_elli2.bin",
additionally writes the number of tries it took to find valid seeds to file "out_hemmert_elli2_tries.txt"
Default value of n is 100 and m is 10^3.
Approximate time to generate 10^3 seeds is 60 seconds.

Example use:

    sage ./backdoor_hemmert_elli2.sage

    sage ./backdoor_hemmert_elli2.sage [n] [m]

    sage ./backdoor_hemmert_elli2.sage [n] [m] [output dir]
        Note! dir must exist before running the program
'''

import sys
import time
import secrets
import elligator.elligator2 as elli

def dir_map(r):
    ''' Wrapper to handle type conversions'''
    _r = elli.GF(int(r))
    u, v, = elli.dir_map(_r)
    return (u.to_num(), v.to_num())


def rev_map(u, v):
    ''' Wrapper to handle type conversions'''
    _u = elli.GF(int(u))
    _v = elli.GF(int(v))
    r = elli.rev_map(_u, _v.is_negative())
    if r:
        return r.to_num()
    return None


def ecdh_key_pair(q, G):
    '''
    Generate an Elliptic Curve Diffie Hellman key pair.
    '''
    sk = secrets.randbelow(q)
    pk = sk * G
    return (pk, sk)


def seed_gen(p, Q, R, pk_a):
    '''
    Generate backdoored seeds.
   
    p    (int)  : prime order subgroup size
    Q    (Point): generator of entire curve
    R    (Point): generator of subgroup of size 4
    pk_a (Point): adversary public key (=yG)

    Returns: (public seed, private seed)
    '''
    i = 0
    seed_pub = None
    seed_priv = None
    while True:
        i +=1
        if i > 100:
            print("Maximum number of tries reached")
            exit()

        b = secrets.randbelow(int(4*p))
        r = secrets.randbelow(4)

        im_pub = b*Q
        im_priv = r*R + b*pk_a

        # Try to compute the preimage
        pub_u  =  im_pub[0]
        pub_v  =  im_pub[1]
        priv_u =  im_priv[0]
        priv_v =  im_priv[1]

        seed_pub  = rev_map(pub_u, pub_v)
        seed_priv = rev_map(priv_u, priv_v)
        
        if seed_pub and seed_priv:
            break

    return seed_pub, seed_priv, i


def seed_retrival(curve, seed_pub, sk_a, R):
    '''
    Retrive the private seed from the public.
    
    curve    (Curve): elliptic curve
    seed_pub (Int)  : public seed
    sk_a     (Point): adversary secret key

    Returns : retrived private seed
    '''
    # Generate A from seed_pub
    u, v = dir_map(seed_pub)
    assert curve.is_x_coord(u)
    B = curve((u, v, 1))
    C = sk_a * B
    valid = []
    for r in range(0, 4):
        sk = r*R + C
        sk_u = sk[0]
        sk_v = sk[1]
        if seed_priv := rev_map(sk_u, sk_v):
            # TODO: Generate s and e from seed_priv
            # If b == As + e mod q return seed_priv
            valid.append(seed_priv)

    return valid


def get_generators(curve):
    '''
    Returns: (
        G : Generator of entire curve,
        R : Generator of subgroup of size 4
        nr_points: the number of points on the curve
    )
    '''
    nr_points = curve.count_points()
    _, Q = curve.lift_x(8, True) # We choose the point with "positive" y
    assert Q.order() == nr_points
    R = Q * (nr_points // 4)
    assert R.order() == 4
    return Q, R, nr_points


def test_backdoor(curve):
    '''
    Test the backdoor mechanism on curve: y^2 = x^3 + Ax^2 + Bx 
    over finite field of size q.
    '''
    Q, R, nr_points = get_generators(curve)

    pk_a, sk_a = ecdh_key_pair(nr_points, Q)
    seed_pub, seed_priv, nr_tries = seed_gen(nr_points / 4, Q, R, pk_a)
    print(f'Took {nr_tries} tries to find valid seeds')
    # TODO: Use seeds to generate actual key
    possible_seeds = seed_retrival(curve, seed_pub, sk_a, R)

    print("Results")
    print("---------------------------")
    res = False
    for i, s in enumerate(possible_seeds):
        match = s == seed_priv #or s == mod(-seed_priv, q)
        res |= match
        print(f'Seed {i}: match: {match}, value: {s}')
    
    assert res, 'Seed retrival failed'


def test_backdoor(curve, nr_tests):
    '''
    Test the backdoor mechanism on curve: y^2 = x^3 + Ax^2 + Bx 
    over finite field of size q, multiple times.
    '''
    Q, R, nr_points = get_generators(curve)
    pk_a, sk_a = ecdh_key_pair(nr_points, Q)
    success = 0
    start = time.time()
    for i in range(0, nr_tests):
        seed_pub, seed_priv, nr_tries = seed_gen(nr_points / 4, Q, R, pk_a)
        possible_seeds = seed_retrival(curve, seed_pub, sk_a, R)
        res = False
        for i, s in enumerate(possible_seeds):
            match = s == seed_priv
            res |= match

        if (res):
            success += 1
    
    print(f"Successful tests: {success}/{nr_tests}")
    print(f"Time taken: {round(time.time() - start, 2)} s")


def collect_data(curve, nr_tests, file):
    Q, R, nr_points = get_generators(curve)
    pk_a, sk_a = ecdh_key_pair(nr_points, Q)
    seed_file = open(f"{file}.bin", "wb")
    tries_file = open(f"{file}_tries.txt", "w")
    start = time.time()
    tries = 0
    for i in range(0, nr_tests):
        seed_pub, seed_priv, nr_tries = seed_gen(nr_points / 4, Q, R, pk_a)
        seed_file.write(int(seed_pub).to_bytes(32, 'little'))
        seed_file.write(int(seed_priv).to_bytes(32, 'little'))
        tries_file.write(f"{nr_tries}\n")
        tries += nr_tries

    seed_file.close()
    tries_file.close()

    print(f"Wrote {nr_tests} seed pairs to file {file}")
    print(f"Took {round(tries / nr_tests, 3)} tries to find valid seeds on average. ")
    print(f"Time taken: {round(time.time() - start, 2)} s")


if __name__ == '__main__':
    q = 2**257 - 93
    d = 1088

    # Twisted Montgomery: B_mont*v^2 = u^3 + A_mont*u^2 + u 
    A_mont = 4/(1-d)-2
    B_mont = 4/(1-d)

    # Elligator representation: v^2 = u^3 + A_elli*u^2 + B_elli*u
    A_elli = A_mont*B_mont
    B_elli = B_mont*B_mont

    curve = EllipticCurve(GF(q), [0, A_elli, 0, B_elli, 0])
    
    elli.GF.p = q
    elli.A = elli.GF(int(curve.a2()))
    elli.B = elli.GF(int(curve.a4()))
    elli.Z = elli.GF(-1)

    # ---------------------------------------------------------
    nr_tests = 100
    nr_samples = 1000
    file = "out_hemmert_elli2"

    if len(sys.argv) >= 3:
        nr_tests = int(sys.argv[1])
        nr_samples = int(sys.argv[2])
    
    if len(sys.argv) >= 4:
        dir = sys.argv[3]
        file = dir + '/' + file

    if nr_tests > 0:
        test_backdoor(curve, nr_tests)
    
    if nr_samples > 0:
        collect_data(curve, nr_samples, file)
