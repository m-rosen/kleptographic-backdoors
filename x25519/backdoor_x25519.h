/**
 * Written by Miriam Rosén in 2023
*/
#ifndef BACKDOOR_H
#define BACKDOOR_H

#include "monocypher/monocypher.h"
#include "monocypher/utils.h"


/**
 * Geneate adversary's key pair. (Done once, not part of deployed system)
 * Key length is 256 bits (or 32 bytes)
*/
void backdoor_init(uint8_t pk[32], uint8_t sk[32]);


/**
 * Generate seeds containing the backdoor
*/
int backdoor_seed_gen(uint8_t seed_pub[32], uint8_t seed_priv[32]);


/**
 * Retrive users private key, using adversary's private key and user's public key.
*/
void backdoor_key_retrival(uint8_t seed_priv[8][32], uint8_t seed_pub[32], uint8_t sk_a[32]);

#endif