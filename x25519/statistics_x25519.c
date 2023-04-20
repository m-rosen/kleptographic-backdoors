/**
 * Written by Miriam Rosén in 2023
*/
#include <stdio.h>
#include <string.h>
#include <time.h>
#include "backdoor_x25519.h"

// NTEST is defined in the makefile
#define SEED_LEN 32

/**
 * Runs seed generation repeatedly and writes seeds to file.
*/
int main(int argc, char **argv)
{
  uint8_t sk_a[SEED_LEN]; // Adversary secret key
  uint8_t pk_a[SEED_LEN]; // Adversary public key

  uint8_t seed_priv[SEED_LEN]; // Secret seed (x*sk_a*P)
  uint8_t seed_pub[SEED_LEN];  // Public seed (x*P)

  FILE *seed_file = fopen("out_x25519.bin", "wb");
  FILE *tries_file = fopen("out_x25519_tries.txt", "w");

  clock_t t;
  t = clock();

  // Adversary generates key pair
  backdoor_init(pk_a, sk_a);
  int nr_tries = 0;
  int max_tries = 0;
  for (int i = 0; i < NTEST; i++)
  {
    int res = backdoor_seed_gen(seed_pub, seed_priv);
    if (res)
      nr_tries += res;
    else
    {
      printf("ERROR: Seed generation failed, ran more than 100 times.\n");
      return 1;
    }

    if (res > max_tries)
      max_tries = res;

    fwrite(seed_pub, SEED_LEN, 1, seed_file);
    fwrite(seed_priv, SEED_LEN, 1, seed_file);
    fprintf(tries_file, "%d\n", res);
  }

  fclose(seed_file);
  fclose(tries_file);

  printf("Wrote %d seed pairs to file x25519/out_x25519.bin\n", NTEST);
  printf("Average %.2f tries to find valid seeds, max %d times.\n", (float) nr_tries / NTEST, max_tries);
  printf("Time taken: %.3fs\n", (float)(clock() - t)/CLOCKS_PER_SEC);
  
  return 0;
}