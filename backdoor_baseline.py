''' Collect samples from Secrets.randbits

Written by Miriam Rosén in 2023

Generates n random seed pairs, and writes them to "out_baseline.bin"
Default value of n is 10^3.
Approximate time to generate 10^3 seeds is < 1 second.

Example use:

    python ./backdoor_baseline.py

    python ./backdoor_baseline.py [n]

    python ./backdoor_baseline.py [n] [output dir]
        Note! dir must exist before running the program
'''


import sys
import time
import secrets

def randomness_baseline(n, file):
    start = time.time()
    max_val = 2**256 - 1
    fd = open(file, 'wb')
    for _ in range(0, n):
        rand = secrets.randbits(256*2)
        fd.write(rand.to_bytes(64, 'little'))
    fd.close()
    print(f"Wrote {n} random seed pairs to file {file}")
    print(f"Time taken: {round(time.time() - start, 2)} s")


if __name__ == "__main__":
    nr_tests = 1000
    file = "out_baseline.bin"

    if len(sys.argv) >= 2:
        nr_tests = int(sys.argv[1])

    if len(sys.argv) >= 3:
        dir = sys.argv[2]
        file = dir + '/' + file

    randomness_baseline(nr_tests, file)