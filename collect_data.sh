
# Written by Miriam Rosén in 2023

#!/bin/bash

echo "Input number of seed pairs to generate for each backdoor variant"
read nr_samples

dir=data
mkdir -p $dir

awk "BEGIN {printf \"Generating $nr_samples seed pairs for each backdoor variant, expected exec time %.2f min\n\",
    ((1/1000 + 6/1000 + 20/1000 + 60/1000 + 1/1000)*$nr_samples/60)}"

echo "Continue?"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) break;;
        No ) exit;;
    esac
done

echo "Started at $(date)"

python backdoor_baseline.py $nr_samples $dir
python backdoor_lkr.py 0 $nr_samples $dir
python hemmert/backdoor_hemmert_elli1.py 0 $nr_samples $dir
sage hemmert/backdoor_hemmert_elli2.sage 0 $nr_samples $dir
cd x25519
make run_statistics NTEST=$nr_samples
cd ..
