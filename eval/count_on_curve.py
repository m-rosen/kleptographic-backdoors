'''
    Written by Miriam Rosén in 2023
'''
from ecpy.curves import Curve
import sys

NR_SAMPLES = None


def read_seed(f):
    return int.from_bytes(f.read(32), 'little')


def read_seeds(file_name, nr_seed_pairs):
    f = open(file_name, "rb")
    public = []
    private = []
    i = 0
    while i < nr_seed_pairs:
        public.append(read_seed(f))
        private.append(read_seed(f))
        i += 1
    f.close()
    return public, private


def count_on_curve(data, curve_name):
    ''' Available curves found with cCurve.get_curve_names()
        for example: secp256k1 or Curve25519 '''
    curve = Curve.get_curve(curve_name)
    count = len(list(filter(lambda x: curve.y_recover(x) != None, data)))
    return round(count/NR_SAMPLES, 3)


if __name__ == '__main__':

    if len(sys.argv) == 2:
        NR_SAMPLES = int(sys.argv[1])
    else:
        print("Err: Usage count_on_curve [nr samples]")
        exit()

    public_baseline, private_baseline = read_seeds("../data/out_baseline.bin", NR_SAMPLES)
    public_lkr,      private_lkr      = read_seeds("../data/out_lkr.bin", NR_SAMPLES)
    public_hemmert,  private_hemmert  = read_seeds("../data/out_hemmert_elli2.bin", NR_SAMPLES)
    public_x25519,   private_x25519   = read_seeds("../data/out_x25519.bin", NR_SAMPLES)
    
    combined_baseline = public_baseline + private_baseline
    combined_lkr = public_lkr + private_lkr
    combined_x25519 = public_x25519 + private_x25519
    combined_hemmert = public_hemmert + private_hemmert

    # Count number of points on secp256k1
    print("Proportion of points on: secp256k1")
    print(f"Baseline: {count_on_curve(public_baseline, 'secp256k1')}")
    print(f"LKR     : {count_on_curve(public_lkr, 'secp256k1')}")
    print(f"Hemmert : {count_on_curve(public_hemmert, 'secp256k1')}")
    print(f"X25519  : {count_on_curve(public_x25519, 'secp256k1')}")
    print()

    # Count number of points on Curve25519
    print("Proportion of points on: Curve25519")
    print(f"Baseline: {count_on_curve(public_baseline, 'Curve25519')}")
    print(f"LKR     : {count_on_curve(public_lkr, 'Curve25519')}")
    print(f"Hemmert : {count_on_curve(public_hemmert, 'Curve25519')}")
    print(f"X25519  : {count_on_curve(public_x25519, 'Curve25519')}")
