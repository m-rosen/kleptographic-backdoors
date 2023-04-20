/**
 * Written by Miriam Rosén in 2023
*/
#include <stdio.h>
#include <string.h>
#include "backdoor_x25519.h"
#include "monocypher/utils.h"
#include <time.h>

/*
    Tests the basic functionality of the backdoor, not integrated with actual Kyber key generation.
*/

#define KEY_LEN 32

int test_verbose()
{
    uint8_t sk_a  [KEY_LEN]; // Adversary secret key
    uint8_t pk_a  [KEY_LEN]; // Adversary public key
    
    uint8_t seed_priv  [KEY_LEN]; // Secret seed (x*sk_a*P)
    uint8_t seed_pub   [KEY_LEN]; // Public seed (x*P)

    uint8_t recovered_seed_priv [8][KEY_LEN];  // Recovered secret seed (pk_a*seed_pub = pk_a*x*P)

    // Adversary generates key pair
    backdoor_init(pk_a, sk_a);

    printf("pk_a: ");
    print_vector(pk_a, KEY_LEN);
    
    printf("sk_a: ");
    print_vector(sk_a, KEY_LEN);

    // User generates seeds
    backdoor_seed_gen(seed_pub, seed_priv);

    printf("seed_pub:  ");
    print_vector(seed_pub, KEY_LEN);

    printf("seed_priv: ");
    print_vector(seed_priv, KEY_LEN);

    // Adversary reconstructs private seed from public seed
    backdoor_key_retrival(recovered_seed_priv, seed_pub, sk_a);
    for (int i = 0; i < 8; i++)
    {
        // Compare with real private seed
        if (memcmp(seed_priv, recovered_seed_priv[i], KEY_LEN) == 0)
        {   
            printf("i = %d\n", i);
            printf("Successfully recovered seed_priv: ");
            print_vector(recovered_seed_priv[i], KEY_LEN);
            return 0;
        }
    }
    
    printf("ERROR: failed to recover the private seed\n");
    return 1;
}


int test_multiple(int nr_tests)
{
    uint8_t sk_a  [KEY_LEN]; // Adversary secret key
    uint8_t pk_a  [KEY_LEN]; // Adversary public key
    
    uint8_t seed_priv  [KEY_LEN]; // Secret seed (x*sk_a*P)
    uint8_t seed_pub   [KEY_LEN]; // Public seed (x*P)

    uint8_t recovered_seed_priv [8][KEY_LEN];  // Recovered secret seed (pk_a*seed_pub = pk_a*x*P)

    backdoor_init(pk_a, sk_a);
    int nr_success = 0;
    clock_t t = clock();
    for (int i = 0; i < nr_tests; i++)
    {
        // User generates seeds
        backdoor_seed_gen(seed_pub, seed_priv);
        // Adversary reconstructs private seed from public seed
        backdoor_key_retrival(recovered_seed_priv, seed_pub, sk_a);
        for (int i = 0; i < 8; i++)
        {
            // Compare with real private seed
            if (memcmp(seed_priv, recovered_seed_priv[i], KEY_LEN) == 0)
            {   
                nr_success++;
                break;
            }
        }    
    }

    printf("Successful tests: %d/%d\n", nr_success, nr_tests);
    printf("Time taken: %f s\n", (float)(clock() - t)/CLOCKS_PER_SEC);
    
    return nr_success;
}

int main()
{
    test_verbose();
    test_multiple(1000);
}