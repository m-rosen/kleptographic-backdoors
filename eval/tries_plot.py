'''
    Written by Miriam Rosén in 2023
'''
import matplotlib.pyplot as plt
import numpy as np
import sys

NR_SAMPLES = None

def configure_font():
    plt.rcParams.update({'figure.autolayout': True})
    SMALL_SIZE = 14
    MEDIUM_SIZE = 16
    BIGGER_SIZE = 18

    plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
    plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
    plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
    plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
    plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
    plt.rc('legend', fontsize=MEDIUM_SIZE)    # legend fontsize
    plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title


def read_file(src):
    file = open(src, 'r')
    tries = []
    for i, line in enumerate(file):
        tries.append(int(line))
        if i == NR_SAMPLES - 1:
            break
    file.close()
    return tries


def plot_combined(a, b, c, dst):
    max_val = max([max(a), max(b), max(c)])
    bins = [ i for i in range(1, max_val + 2)]
    counts_a, _ = np.histogram(a, bins=bins)
    counts_b, _ = np.histogram(b, bins=bins)
    counts_c, _ = np.histogram(c, bins=bins)

    counts_a = list(map(lambda x: x/NR_SAMPLES, counts_a))
    counts_b = list(map(lambda x: x/NR_SAMPLES, counts_b))
    counts_c = list(map(lambda x: x/NR_SAMPLES, counts_c))

    x = np.array([i for i in range(1, 15 + 1)])
    plt.bar(x - 0.3, counts_a[:15], 0.3, label = 'Hemmert w. Elligator 1')
    plt.bar(x, counts_b[:15], 0.3, label = 'Hemmert w. Elligator 2')
    plt.bar(x + 0.3, counts_c[:15], 0.3, label = 'X25519')

    distr = [ (3/4)**(n-1)*(1/4) for n in x]
    plt.plot(x, distr, color='black', label= r'(0.25)(0.75)$^{n-1}$')

    plt.legend()
    plt.xticks([i * 5 for i in range(0, 4)])
    # plt.yticks([i * 1000 for i in range(0, 4)])
    plt.xlabel("Number of tries")
    plt.ylabel("Proportion")

    plt.savefig(dst)
    plt.close()


if __name__ == "__main__":

    if len(sys.argv) == 2:
        NR_SAMPLES = int(sys.argv[1])
    else:
        print("Err: Usage tries_plot [nr samples]")
        exit()

    configure_font()
    
    hemmert_elli1 = read_file("../data/out_hemmert_elli1_tries.txt")
    hemmert_elli2 = read_file("../data/out_hemmert_elli2_tries.txt")
    x25519 = read_file("../data/out_x25519_tries.txt")
    plot_combined(
        hemmert_elli1,
        hemmert_elli2,
        x25519,
        "../data/tries_combined.pdf"
    )

    # Print global stats
    print(f'Max Hemmert Elli1 {max(hemmert_elli1)}')
    print(f'Max Hemmert Elli2 {max(hemmert_elli2)}')
    print(f'Max X25519        {max(x25519)}')