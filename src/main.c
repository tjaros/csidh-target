#include "hal.h"
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#include "fp.h"
#include "csidh.h"
#include "mont.h"
#include "uint.h"

#include "simpleserial.h"

public_key pk = {.A.c = {0}};
private_key sk = {.e = {0}};
public_key result;
uint8_t num_batches = 3;
int8_t max_exponent[NUM_PRIMES] = {2};
unsigned int num_isogenies = 2;
uint8_t my = 0;

uint8_t set_public(uint8_t cmd, uint8_t scmd, uint8_t dlen, uint8_t* data)
{
    if (scmd == 0x01)
        pk = base;
    else
        memcpy(pk.A.c, (void *) data, 64);
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
    simpleserial_put('r', (uint8_t) sizeof(result.A.c), (void *) result.A.c);

    pk = result;

    if (error != 0)
        return 0x10+error;
    return 0;
}

void api(void)
{
    // Set/Get public
    simpleserial_addcmd('1', 64, set_public);
    simpleserial_addcmd('2', 0, get_public);
    // Set/Get private
    simpleserial_addcmd('3', NUM_PRIMES, set_secret);
    simpleserial_addcmd('4', 0, get_secret);
    // csidh does not need arguments
    simpleserial_addcmd('5', 0, run_csidh);

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
