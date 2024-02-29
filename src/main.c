#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

#include "fp.h"
#include "csidh.h"
#include "mont.h"
#include "uint.h"
#include "parametrization.h"


public_key pk = {.A.c = {0}};
private_key sk = {.e = {0}};
public_key result;
#ifdef F419
uint8_t num_batches = 1;
#else
uint8_t num_batches = 3;
#endif
int8_t max_exponent[NUM_PRIMES];
unsigned int num_isogenies;
uint8_t my = 0;

uint8_t set_public(uint8_t* data)
{
    memcpy(pk.A.c, (void *) data, LIMBS * 8);
    return 0;
}
 
uint8_t get_public()
{
    printf("\npublic: ");
    for (int i = 0; i < sizeof(pk.A.c); i++)
        printf("%x", ((uint8_t*) pk.A.c)[i]);
    printf("\n");
    return 0;
}

uint8_t set_secret(uint8_t cmd, uint8_t scmd, uint8_t dlen, uint8_t* data)
{
    memcpy(sk.e, (void *) data, NUM_PRIMES);
    return 0;
}

uint8_t get_secret()
{
    printf("\nsecret: ");
    for (int i = 0; i < sizeof(sk.e); i++)
        printf("%x", ((uint8_t*) sk.e)[i]);
    printf("\n");
    return 0;
}

// Runs a group action on current public key and the secret
uint8_t run_csidh()
{
    uint8_t error = csidh(&result, &pk, &sk, num_batches, max_exponent, num_isogenies, my);
    pk = result;


    if (error != 0)
        return 0x10+error;
    return 0;
}

#ifdef DBG
void test_ecc(void)
{
    // Here we just do some simple ec multiplication to check if we got correct results
    proj P = {.x={{119}}, .z={{1}}};
    proj A = {.x={{0}}, .z={{1}}};
    proj Q = {{{0}}};
    uint_c k = {{1}};

    char str[1024];
    sprintf(str, 
    "[DBG] xMUL P=(%lu, %lu) A=%lu Q=(%lu, %lu) k=%lu\n",
    (long unsigned int)P.x.c[0],
    (long unsigned int)P.z.c[0],
    (long unsigned int)A.x.c[0],
    (long unsigned int)Q.x.c[0],
    (long unsigned int)Q.z.c[0],
    (long unsigned int)k.c[0]
    );

    uart_puts(str);
    xMUL(&Q, &A, &P, &k);

    sprintf(str, 
    "[DBG] xMUL P=(%lu, %lu) A=%lu Q=(%lu, %lu) k=%lu\n",
    (long unsigned int)P.x.c[0],
    (long unsigned int)P.z.c[0],
    (long unsigned int)A.x.c[0],
    (long unsigned int)Q.x.c[0],
    (long unsigned int)Q.z.c[0],
    (long unsigned int)k.c[0]
    );
    uart_puts(str);

}

uint8_t tests(uint8_t cmd, uint8_t scmd, uint8_t dlen, uint8_t* data)
{
    test_ecc();
    return 0;
}

#endif

int main(void)
{
    printf("Running CSIDH with %d limbs\n", LIMBS);

    max_exponent[0] = 5;
    max_exponent[1] = 5;
    max_exponent[2] = 5;
    num_isogenies = (unsigned int) 15;
    sk.e[0] = -1;
    sk.e[1] = -1;
    sk.e[2] = -1;

    run_csidh();

    get_public();

    num_isogenies = (unsigned int) 15;
    sk.e[0] = 0;
    sk.e[1] = 1;
    sk.e[2] = 1;

    run_csidh();

    get_public();

    num_isogenies = (unsigned int) 15;
    sk.e[0] = 1;
    sk.e[1] = 0;
    sk.e[2] = 0;

    run_csidh();

    get_public();
 
}
