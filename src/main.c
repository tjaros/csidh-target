#include "hal.h"
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

#include "fp.h"
#include "csidh.h"
#include "mont.h"
#include "uint.h"
#include "parametrization.h"

#include "simpleserial.h"
#include "hal.h"




public_key pk = {.A.c = {0}};
private_key sk = {.e = {0}};
public_key result;
#ifdef F419
uint8_t num_batches = 1;
#else
uint8_t num_batches = 3;
#endif
int8_t max_exponent[NUM_PRIMES] = {1};
unsigned int num_isogenies = 1;
uint8_t my = 0;

uint8_t set_public(uint8_t cmd, uint8_t scmd, uint8_t dlen, uint8_t* data)
{
    if (scmd == 0x01)
        pk = base;
    else
        memcpy(pk.A.c, (void *) data, LIMBS * 8);
    return 0;
}
 
uint8_t get_public(uint8_t cmd, uint8_t scmd, uint8_t dlen, uint8_t* data)
{
    simpleserial_put('r', (uint8_t) sizeof(pk.A.c), (void *) pk.A.c);
    return 0;
}

uint8_t set_secret(uint8_t cmd, uint8_t scmd, uint8_t dlen, uint8_t* data)
{
    memcpy(sk.e, (void *) data, NUM_PRIMES);
    return 0;
}

uint8_t get_secret(uint8_t cmd, uint8_t scmd, uint8_t dlen, uint8_t* data)
{
    simpleserial_put('r', (uint8_t) sizeof(sk.e), (void *) sk.e);
    return 0;
}

// Runs a group action on current public key and the secret
uint8_t run_csidh(uint8_t cmd, uint8_t scmd, uint8_t dlen, uint8_t* data)
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

void api(void)
{
    // Set/Get public
    simpleserial_addcmd('1', LIMBS * 8, set_public);
    simpleserial_addcmd('2', 0, get_public);
    // Set/Get private
    simpleserial_addcmd('3', NUM_PRIMES, set_secret);
    simpleserial_addcmd('4', 0, get_secret);
    // csidh does not need arguments
    simpleserial_addcmd('5', 0, run_csidh);
    #ifdef DBG
    simpleserial_addcmd('6', 0, tests);
    #endif

    while (1)
    {
        simpleserial_get();
    }
}

int main(void)
{
    platform_init();
    init_uart();

    putch('r');
    putch('e');
    putch('s');
    putch('e');
    putch('t');


    simpleserial_init();
    api();
}
