/**
 * Written by Miriam Rosén in 2023
*/
#ifndef TEST_RETRIVAL
#define TEST_RETRIVAL

#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include "kem.h"
#include "indcpa.h"
#include "randombytes.h"
#include "../backdoor_x25519.h"


int test_retrival(uint8_t* sk_a)
{
	uint8_t pk_u[CRYPTO_PUBLICKEYBYTES];
	uint8_t sk_u[CRYPTO_SECRETKEYBYTES];

	uint8_t unpacked_pk_u[CRYPTO_PUBLICKEYBYTES];
	uint8_t public_seed[CRYPTO_BYTES];
	uint8_t recovered_seed_priv [8][CRYPTO_BYTES];

	uint8_t seed[2*CRYPTO_BYTES];
	uint8_t pk_regen[CRYPTO_PUBLICKEYBYTES];
	uint8_t sk_regen[CRYPTO_SECRETKEYBYTES];

	// User generates a public key
	crypto_kem_keypair(pk_u, sk_u);

	// Adversary extracts public seed from the public key
	unpack_pk(unpacked_pk_u, public_seed, pk_u);
	
	// Adversary derives secret seed
	backdoor_key_retrival(recovered_seed_priv, public_seed, sk_a);

	int success = 0;
	memcpy(seed, public_seed, CRYPTO_BYTES);
	for (int i = 0; i < 8; i++)
    {
        // Use public_seed + recevered_seed_priv[i] to generate a keypair
		memcpy(seed + CRYPTO_BYTES, recovered_seed_priv[i], CRYPTO_BYTES);
		crypto_kem_keypair_regen(pk_regen, sk_regen, seed);
		
		// Compare to the real public keys
		if (memcmp(pk_u, pk_regen, CRYPTO_PUBLICKEYBYTES) == 0)
		{	
			// If we have a match increment success
			success ++;
			// Verify that the secret key also matches
			if (memcmp(sk_u, sk_regen, CRYPTO_PUBLICKEYBYTES) == 1)
			{
				printf("ERROR: Public matched but not private");
				return 1;
			}
		}
    }
	
	if (success == 1) // Assert that we find a unique match
		return 0;
	
	printf("Error: Could not recover the user's key, sucess = %d", success);
	return 0;
}

#endif