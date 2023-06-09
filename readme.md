# Kleptographic backdoors

This project contains the source files of four variants of kleptographic backdoors. This work was part of my master thesis project *Experimental Evaluation of Kleptographic Backdoors in LWE-based KEMs* and the goal was to implement the backdoor constructions described by Hemmert in [*How to backdoor LWE-like cryptosystems*](https://eprint.iacr.org/2022/1381) and by Yang et al. in [*Lattice Klepto Revisited*](https://dl.acm.org/doi/10.1145/3320269.3384768).

All four vaiants have verification tests, to see that secrets can be correctly retrived, and scripts for generating data to be used for statistical testing.

The script ``collect_data.sh`` can be used to collect samples form all backdoor variants. **NOTE!** Before running ``collect_data.sh`` sage and ECpy must be installed, and a the folder ``x25519/build/`` must be created.

All testing has been done on Ubuntu running in WSL.

## Lattice Klepto Revisited (LKR)

- file: backdoor_lkr.py
- dependencies: python3, ECPy

## How to backdoor LWE-like cryptosystems (Hemmert)

### Elligator implementation

An extension of Loup Vaillant's [refence implementation](https://elligator.org/src/) of Elligator 2 and an implmentation of Elligator 1 is available in ``hemmert/elligator/``.


### Backdoor with Elligator 1

- file: hemmert/backdoor_hemmert_elli1.py
- dependencies: python3, ECPy, elligator1.py


### Backdoor with Elligator 2

- file: hemmert/backdoor_hemmert_elli2.sage
- dependencies: python3, SageMath, elligator2.py


## A new backdoor (X25519)

Makefile has options:
- run_tests
- run_statistics
- dependencies: monocypher library (included)

This backdoor was integrated in the Kyber [reference implementation](https://github.com/pq-crystals/kyber), to test the backdoor with Kyber run:

    ~/x25519/kyber_ref/: make run_backdoor_all

If all tests run without error messages the tests passes. **NOTE!** Before running the test you must run:

    ~/x25519/: make kyber_obj

## Evaluation

The Evaluation folder contains scripts for analyzing the data generated by the backdoors. **NOTE!** The X25519 files need to be moved to the data folder manually.
Example use:

    python count_on_curve.py [nr samples]
    python tries_plot.py [nr samples]
    python sts_plots.py [path to NIST STS finalAnalysisReport.txt file]

# Files:
    - eval/
        - count_on_curve.py
        - nist_sts_parse.py
        - nist_sts_plots.py
        - tries_plot.py

    - hemmert/
        - elligator/
            - core.py
            - elligator1.py
            - elligator2.py

        - backdoor_hemmert_elli1.py
        - backdoor_hemmert_elli2.sage
        - generator.sage
    
    - X25519/    
        - kyber_ref/ # Unmodified files are omitted
            - incpa.h, indcpa.c
            - kem.h, kem.c
            - test_backdoor_speed.c
            - test_kyber.c
            - test_retrival.h
            - Makefile
            - ...
        
        - monocypher/
        - backdoor_x25519.h, backdoor_x25519.c
        - statistics_x25519.c
        - test_x25519.c
        - Makefile
    
    - backdoor_baseline.py
    - backdoor_lkr.py
    - collect_data.sh
    - readme.md

