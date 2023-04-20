/**
 * Written by Miriam Rosén in 2023
*/
#include <time.h>
#include <stdio.h>

#include "kem.h"
#include "indcpa.h"

#ifdef COUNTERMEASURE
#include "symmetric.h"
#include <string.h>
#endif

#ifdef BACKDOOR
#include "../backdoor_x25519.h"
#endif

#define NR_TESTS 100000 //10^4

int main(void)
{
    uint8_t pk_u[CRYPTO_PUBLICKEYBYTES];
	uint8_t sk_u[CRYPTO_SECRETKEYBYTES];

#ifdef BACKDOOR
    uint8_t pk_a[32];
    uint8_t sk_a[32];
    backdoor_init(pk_a, sk_a);
#endif

    clock_t t;
    t = clock();
#ifdef COUNTERMEASURE
    int err = 0;
#endif
    for (size_t i = 0; i < NR_TESTS; i++)
    {
        // User generates a public key
        crypto_kem_keypair(pk_u, sk_u);
#ifdef COUNTERMEASURE
        hash_g(pk_u, pk_u, KYBER_SYMBYTES);
        err = 0;
        if(memcmp(pk_u, sk_u, 2*KYBER_SYMBYTES) != 0)
            err = 1;
#endif
    }

#ifdef BACKDOOR
    printf("BACKDOOR: Time taken: %fs\n", (float)(clock() - t)/CLOCKS_PER_SEC);
#elif defined COUNTERMEASURE
    printf("COUNTERMEASURE: Time taken: %fs\n", (float)(clock() - t)/CLOCKS_PER_SEC);
    printf("%d\n", err); // Print err in order to make sure compiler does not optimize away the "validation" check
#else
    printf("NORMAL: Time taken: %fs\n", (float)(clock() - t)/CLOCKS_PER_SEC);
#endif

}