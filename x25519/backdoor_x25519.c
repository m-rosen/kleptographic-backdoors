/**
 * Written by Miriam Rosén in 2023
*/
#include "monocypher/monocypher.h"
#include "monocypher/utils.h"
#include "backdoor_x25519.h"
#include <bsd/stdlib.h> // to access arc4random_buf
#include <string.h> // for memcpy

static uint8_t pk_a[32];

/**
 * Generate adversary's key pair. (Done once, not part of deployed system)
 * Key length is 256 bits (or 32 bytes)
 * @out sk = y, pk = yP
*/
void backdoor_init(uint8_t pk[32], uint8_t sk[32])
{
    arc4random_buf(sk, 32);
    crypto_x25519_public_key(pk, sk);
    memcpy(pk_a, pk, 32); // Store adversay public key in system
}


/**
 * Generate seeds containing the backdoor
 * seed_pub = iota^-1(xP), seed_priv = x*pk_a = xyP
 * returns: number of attempts to find valid seed pair
*/
int backdoor_seed_gen(uint8_t seed_pub[32], uint8_t seed_priv[32])
{   
    uint8_t sk [32];   /* Secret key output  */
    uint8_t tweak = 0; /* Random tweak input */
    uint8_t tweak_priv = 0; /* Random tweak input */
    arc4random_buf(&tweak, 1);
    arc4random_buf(&tweak_priv, 1);
    int i = 0;
    for(;;) {
        i++;
        arc4random_buf(sk, 32);
        crypto_x25519_dirty_small(seed_pub, sk);
        if (crypto_curve_to_hidden(seed_pub, seed_pub, tweak) == 0)
        {
            /* Compute shared secret */
            crypto_x25519(seed_priv, sk, pk_a);

            /* Try to hide the shared secret */
            if (crypto_curve_to_hidden(seed_priv, seed_priv, tweak_priv) == 0)
                break;
        }
        if (i > 100)
            return 0;
    }

    /* Wipe secrets if they are no longer needed */
    crypto_wipe(sk, 32);
    return i;
}

static uint8_t TWEAK[8] = { 0x00, 0x01, 0x40, 0x41, 0x80, 0x81, 0xC0, 0xC1 };

/**
 * Retrive possible values of users private key, using adversary's private key and user's public key.
*/
void backdoor_key_retrival(uint8_t seed_priv[8][32], uint8_t seed_pub[32], uint8_t sk_a[32])
{
    uint8_t their_pk  [32]; /* Their unhidden public key */
    uint8_t unhidden_seed [32];
    crypto_hidden_to_curve(their_pk, seed_pub);
    crypto_x25519(unhidden_seed, sk_a, their_pk);

    for (int i = 0; i < 8; i++)
        crypto_curve_to_hidden(seed_priv[i], unhidden_seed, TWEAK[i]);
}