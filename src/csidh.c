
#include <assert.h>
#include <stdio.h>
#include <string.h>

#include "csidh.h"
#include "fp.h"
#ifdef HAL
#include "hal.h"
#endif
#include "mont.h"
#include "parametrization.h"
#include "randombytes.h"
#include "uint.h"

const public_key base = {0}; /* A = 0 */

// TODO remove
// int8_t error = 0;
#ifdef DBG
void uart_puts(char *s)
{
    while (*s)
    {
        putch(*(s++));
    }
}
#endif

extern unsigned long long overflowcnt;
extern unsigned long long startcnt;

/* get priv[pos] in constant time  */
int32_t lookup(size_t pos, int8_t const *priv)
{
    int b;
    int8_t r = priv[0];
    for (size_t i = 1; i < NUM_PRIMES; i++)
    {
        b = isequal(i, pos);
        // ISEQUAL(i, pos, b);
        // b = (uint8_t)(1-((-(i ^ pos)) >> 31));
        cmov(&r, &priv[i], b);
        // CMOV(&r, &priv[i], b);
    }
    return r;
}

/* check if a and b are equal in constant time  */
uint32_t isequal(uint32_t a, uint32_t b)
{
    // size_t i;
    uint32_t r        = 0;
    unsigned char *ta = (unsigned char *)&a;
    unsigned char *tb = (unsigned char *)&b;
    r                 = (ta[0] ^ tb[0]) | (ta[1] ^ tb[1]) | (ta[2] ^ tb[2]) | (ta[3] ^ tb[3]);
    r                 = (-r);
    r                 = r >> 31;
    return (int)(1 - r);
}

/* decision bit b has to be either 0 or 1 */
void cmov(int8_t *r, const int8_t *a, uint32_t b)
{
    uint32_t t;
    b = -b; /* Now b is either 0 or 0xffffffff */
    t = (*r ^ *a) & b;
    *r ^= t;
}

void csidh_private(private_key *priv, const int8_t *max_exponent)
{
    memset(&priv->e, 0, sizeof(priv->e));
    for (size_t i = 0; i < NUM_PRIMES;)
    {
        int8_t buf[64];
        randombytes((unsigned char *)buf, sizeof(buf));
        for (size_t j = 0; j < sizeof(buf); ++j)
        {
            if (buf[j] <= max_exponent[i] && buf[j] >= -max_exponent[i])
            {
                priv->e[i] = lookup(j, buf);
                if (++i >= NUM_PRIMES)
                    break;
            }
        }
    }
}

/* compute [(p+1)/l] P for all l in our list of primes. */
/* divide and conquer is much faster than doing it naively,
 * but uses more memory. */
static void cofactor_multiples(proj *P, const proj *A, size_t lower,
                               size_t upper)
{
    assert(lower < upper);

    if (upper - lower == 1)
        return;

    size_t mid = lower + (upper - lower + 1) / 2;

    uint_c cl = uint_1, cu = uint_1;
    for (size_t i = lower; i < mid; ++i)
        uint_mul3_64(&cu, &cu, primes[i]);
    for (size_t i = mid; i < upper; ++i)
        uint_mul3_64(&cl, &cl, primes[i]);

    xMUL(&P[mid], A, &P[lower], &cu);
    xMUL(&P[lower], A, &P[lower], &cl);

    cofactor_multiples(P, A, lower, mid);
    cofactor_multiples(P, A, mid, upper);
}

/* never accepts invalid keys. */
bool validate(public_key const *in)
{
    const proj A = {in->A, fp_1};

    do
    {

        proj P[NUM_PRIMES];
        fp_random(&P->x);
        P->z = fp_1;

        /* maximal 2-power in p+1 */
        xDBL(P, &A, P);
        xDBL(P, &A, P);

        cofactor_multiples(P, &A, 0, NUM_PRIMES);

        uint_c order = uint_1;

        for (size_t i = NUM_PRIMES - 1; i < NUM_PRIMES; --i)
        {

            /* we only gain information if [(p+1)/l] P is non-zero */
            if (memcmp(&P[i].z, &fp_0, sizeof(fp)))
            {

                uint_c tmp;
                uint_set(&tmp, primes[i]);
                xMUL(&P[i], &A, &P[i], &tmp);

                if (memcmp(&P[i].z, &fp_0, sizeof(fp)))
                    /* P does not have order dividing p+1. */
                    return false;

                uint_mul3_64(&order, &order, primes[i]);

                if (uint_sub3(&tmp, &four_sqrt_p, &order)) /* returns borrow */
                    /* order > 4 sqrt(p), hence definitely supersingular */
                    return true;
            }
        }

        /* P didn't have big enough order to prove supersingularity. */
    } while (1);
}

/* compute x^3 + Ax^2 + x */
/*
static void montgomery_rhs(fp *rhs, fp const *A, fp const *x) {
        fp tmp;
        *rhs = *x;
        fp_sq1(rhs);
        fp_mul3(&tmp, A, x);
        fp_add2(rhs, &tmp);
        fp_add2(rhs, &fp_1);
        fp_mul2(rhs, x);
}
*/

/* generates curve points */
void elligator(proj *P, proj *Pd, const fp *A)
{

    fp u2m1, tmp, rhs;
    bool issquare;

#if defined(DETERMINISTIC)
    fp u2 = {{0xf73849b0ce4e064b, 0x94bbfb03237b4a47, 0x467d743c736b034f, 0xb3fee59267e9b9e8, 0x036bafb7d4af3814, 0x05b62c28c87084ce, 0x620a625431f0111e, 0x03d7f790ac52fd83}};
#else
    fp u2;
    fp_random(&u2);
#endif

    fp_sq1(&u2);                // u^2
    fp_sub3(&u2m1, &u2, &fp_1); // u^2 - 1
                                // uart_puts("3\n");
    fp_sq2(&tmp, &u2m1);        // (u^2 - 1)^2
    fp_sq2(&rhs, A);            // A^2
    fp_mul2(&rhs, &u2);         // A^2u^2
    fp_add2(&rhs, &tmp);        // A^2u^2 + u(u^2 - 1)^2
    fp_mul2(&rhs, A);           // (A^2u^2 + u(u^2 - 1)^2)A
    fp_mul2(&rhs, &u2m1);       // (A^2u^2 + u(u^2 - 1)^2)A(u^2 - 1)
                                // uart_puts("4\n");
    fp_set(&P->x, 0);
    fp_add2(&P->x, A);
    fp_set(&P->z, 0);
    fp_add2(&P->z, &u2m1);
    fp_set(&Pd->x, 0);
    fp_sub2(&Pd->x, A);
    fp_mul2(&Pd->x, &u2);
    fp_set(&Pd->z, 0);
    fp_add2(&Pd->z, &u2m1);

    issquare = fp_issquare(&rhs);
    fp_cswap(&P->x, &Pd->x, !issquare);
    fp_cswap(&P->z, &Pd->z, !issquare);
}

#ifdef CM
// Input: A supersingular curve E : Cy^2 = Cx^3 + Ax^2 + Cx over F_p,  and an element u in {2,..., p−1}.
// Output: A pair of points T+ in E[pi - 1] and T- in E[pi + 1], error variable error.
/* generates curve points */
static bool new_elligator(proj *P, proj *Pd, const proj *A, const fp *u, int8_t *ps)
{
    bool error = 0;
    bool b     = false, s1, s2;
    fp a, tmp0, tmp1, tmp2, u2m1, xz;
    // fp_set(&a, 0);
    //  A->x = A and A->z = C
    b = fp_cmp_ct(&A->x, &fp_0); // b <- isequal(A, 0)
    // fp_cadd(&a, &fp_0, u, !b);                // a <- cadd(0, bu)
    fp_cset(&a, u, !b);           // a <- cadd(0, bu)
    fp_sq2(&tmp0, u);             // u^2
    fp_sub3(&u2m1, &tmp0, &fp_1); // u^2 - 1
    fp_mul3(&P->z, &u2m1, &A->z); // Z = C(u^2 - 1)
    fp_mul3(&tmp0, &P->z, &a);    // aC(u^2 - 1)
    fp_add3(&P->x, &A->x, &tmp0); // X = A +aC(u^2 −1)
    fp_cset(&Pd->z, &P->z, 1);    // Z' = C(u^2 - 1)

    // fp_sub3(&tmp0, u, &fp_1);                   // u - 1
    fp_mul3(&tmp2, &a, &A->z);     // aC
    fp_mul3(&tmp1, &u2m1, &tmp2);  // aC (u^2 − 1)
    fp_sq2(&tmp0, u);              // u^2
    fp_mul3(&tmp2, &A->x, &tmp0);  // Au^2
    fp_sub3(&tmp0, &fp_0, &tmp2);  // -Au^2
    fp_sub3(&Pd->x, &tmp0, &tmp1); // X' = −Au^2 −aC (u^2 −1)

    fp_sq2(&tmp0, &P->x);         // X^2
    fp_mul3(&tmp1, &A->z, &tmp0); // CX^2
    fp_mul3(&xz, &P->x, &P->z);   // XZ
    fp_mul3(&tmp0, &A->x, &xz);   // AXZ
    fp_sq2(&a, &P->z);            // Z^2
    fp_mul3(&tmp2, &A->z, &a);    // CZ^2
    fp_add3(&a, &tmp1, &tmp0);    // CX^2 + AXZ
    fp_add3(&tmp0, &a, &tmp2);    // CX^2 + AXZ + + CZ^2
    fp_mul3(&tmp1, &xz, &tmp0);   // XZ(CX^2 + AXZ + + CZ^2)

    s1 = fp_issquare(&tmp1); // s1 <- Legendre symbol(XZ(CX^2 + AXZ + + CZ^2), p)

    fp_sq2(&tmp0, &Pd->x);        // X'^2
    fp_mul3(&tmp1, &A->z, &tmp0); // CX'^2
    fp_mul3(&xz, &Pd->x, &Pd->z); // X'Z'
    fp_mul3(&tmp0, &A->x, &xz);   // AX'Z'
    fp_sq2(&a, &Pd->z);           // Z'^2
    fp_mul3(&tmp2, &A->z, &a);    // CZ'^2
    fp_add3(&a, &tmp1, &tmp0);    // CX'^2 + AX'Z'
    fp_add3(&tmp0, &a, &tmp2);    // CX'^2 + AX'Z' + + CZ'^2
    fp_mul3(&tmp1, &xz, &tmp0);   // X'Z'(CX'^2 + AX'Z' + + CZ'^2)

    s2 = fp_issquare(&tmp1); // s2 <- Legendre symbol(X'Z'(CX'^2 + AX'Z' + CZ'^2), p)

    // fp_cswap(&P->x, &Pd->x, !s1);
    // fp_cswap(&P->z, &Pd->z, !s1);

    error |= !(s1 ^ s2);

    *ps = !(s1 ^ 1); // ps stores information which point is stored in P

    error |= (*ps ^ !(s1 ^ 1)); // check that ps has not been manipulated
    return error;
}
#endif

/* constant-time. */
bool action(public_key *out, public_key const *in, private_key const *priv,
            uint8_t num_batches, int8_t const *max_exponent, unsigned int const num_isogenies, uint8_t const my)
{

#ifdef DBG
    char str[1000];
#endif

#ifdef F419
    uint_c k[1]    = {{{4 * 3 * 5 * 7}}};
    uint_c p_order = {{119}};
#else
    // factors k for different batches
    uint_c k[3] = {{{0x1b5933af628d005c, 0x9d4af02b1d7b7f56, 0x8977a8435092262a, 0xb86302ff54a37ca2, 0xd6e09db2af04d095, 0x5c73f, 0x0, 0x0}},
                   {{0xd97b8b6bc6f6be1c, 0x315872c44ea6e448, 0x1aae7c54fd380c86, 0x237ec4cf2da454a2, 0x3733f9e3d9fea1b4, 0x1fdc0e, 0x0, 0x0}},
                   {{0x629ea97b02169a84, 0xc4b9616a12d48d22, 0x492a10278ad7b45a, 0xc44ac4dce55b87f8, 0x9e12876886632d6e, 0xe0c0c5, 0x0, 0x0}}};

    uint_c p_order = {{0x24403b2c196b9323, 0x8a8759a31723c208, 0xb4a93a543937992b, 0xcdd1f791dc7eb773, 0xff470bd36fd7823b, 0xfbcf1fc39d553409, 0x9478a78dd697be5c, 0x0ed9b5fb0f251816}};
#endif

    int8_t ec = 0, m = 0;
    uint8_t count = 0;
    // uint8_t elligator_index = 0;
    uint8_t last_iso[3], b, ss;
    proj P, Pd, K;
    uint_c cof, l;
    bool finished[NUM_PRIMES]  = {0};
    int8_t e[NUM_PRIMES]       = {0};
    int8_t counter[NUM_PRIMES] = {0};
    int8_t s, ps;
    unsigned int isog_counter = 0;

#ifdef F419
    last_iso[0] = 2;
#else
    // index for skipping point evaluations
    last_iso[0] = 72;
    last_iso[1] = 73;
    last_iso[2] = 71;
#endif

    // e array is the private key
    memcpy(e, priv->e, sizeof(priv->e));

    // counter, is a copy of max exponent array
    memcpy(counter, max_exponent, sizeof(counter));

    proj A = {in->A, fp_1};
#ifdef DBG
    sprintf(str,
            "[DBG] Entered the while isog_counter=%d < num_isogenies=%d loop\n",
            isog_counter,
            num_isogenies);
    uart_puts(str);
#endif
#if defined(HAL) && defined(A1)
    trigger_high();
#endif
    // num_isogenies is a sum of the max_exponent array
    // so we compute the actions untill all values in counter are 0
    while (isog_counter < num_isogenies)
    {
#ifdef DBG
        sprintf(str,
                "[DBG][while isog_counter=%d < num_isogenies=%d] ****************************************\n",
                isog_counter,
                num_isogenies);
        uart_puts(str);
#endif

        m = (m + 1) % num_batches;

        // Compute factor k
        // If num batches = 1, then its executed only at the beginning
        if (count == my * num_batches)
        { // merge the batches after my rounds
            m = 0;
#ifdef F419
            last_iso[0] = 2;
#else
            last_iso[0] = 73; // doesn't skip point evaluations anymore after merging batches
#endif
            uint_set(&k[m], 4); // recompute factor k
            num_batches = 1;

            // no need for constant-time, depends only on randomness
            for (uint8_t i = 0; i < NUM_PRIMES; i++)
            {
                if (counter[i] == 0)
                {
                    uint_mul3_64(&k[m], &k[m], primes[i]);
                }
            }
#ifdef DBG
            sprintf(str,
                    "[DBG] Recomputed the factor k=%lu\n",
                    (long unsigned int)k[0].c[0]);
            uart_puts(str);
#endif
        }

        // Sample the point P, either using elligator, or set it to full order point on A=0
        if (memcmp(&A.x, &fp_0, sizeof(fp)))
        {
            elligator(&P, &Pd, &A.x);
        }
        else
        {
            fp_enc(&P.x, &p_order); // point of full order on E_a with a=0
            fp_sub3(&Pd.x, &fp_0, &P.x);
            P.z  = fp_1;
            Pd.z = fp_1;
        }
#ifdef DBG
        sprintf(str,
                "[DBG] Sampled the point P.x=%lu P.z=%lu Pd.x=%lu Pd.z=%lu\n",
                (long unsigned int)P.x.c[0],
                (long unsigned int)P.z.c[0],
                (long unsigned int)Pd.x.c[0],
                (long unsigned int)Pd.z.c[0]);
        uart_puts(str);
#endif

        xMUL(&P, &A, &P, &k[m]);

        xMUL(&Pd, &A, &Pd, &k[m]);

#ifdef DBG
        sprintf(str,
                "[DBG] Multiplied P, Q by factor k=%lu, P.x=%lu P.z=%lu Pd.x=%lu Pd.z=%lu\n",
                (long unsigned int)k[m].c[0],
                (long unsigned int)P.x.c[0],
                (long unsigned int)P.z.c[0],
                (long unsigned int)Pd.x.c[0],
                (long unsigned int)Pd.z.c[0]);
        uart_puts(str);
#endif
        // No idea what's this for.
        ps = 1; // initialized in elligator

#ifdef DBG
        sprintf(str,
                "[DBG] Entered the for loop\n");
        uart_puts(str);
#endif

        // For each prime, we check if it is done, meaning finished[i] == 1
        // otherwise we perform 1 isogeny to corresponding to the primes[i]
        // and to the correct direction.
        for (uint8_t i = m; i < NUM_PRIMES; i = i + num_batches)
        {
#ifdef DBG
            sprintf(str,
                    "[DBG][for i=%d] ========================================\n",
                    i);
            uart_puts(str);
#endif
            if (finished[i] == true)
            { // depends only on randomness
#ifdef DBG
                sprintf(str,
                        "[DBG] finished[%d] == true\n", i);
#endif
                continue;
            }
            else
            {
                // Compute the cofactor
                cof = uint_1;
                for (uint8_t j = i + num_batches; j < NUM_PRIMES; j = j + num_batches)
                {
                    if (finished[j] == false) // depends only on randomness
                        uint_mul3_64(&cof, &cof, primes[j]);
                }

                ec = lookup(i, e); // check in constant-time if normal or dummy isogeny must be computed
                b  = isequal(ec, 0);
                s  = (uint8_t)ec >> 7; // Sign of the exponent to decide which way the isogeny is computed
                ss = !isequal(s, ps);

                ps = s;

#ifdef DBG
                sprintf(str,
                        "[DBG] Pre Conditional swap: P=(%lu, %lu) and Pd=(%lu, %lu) ss=%d \n",
                        (unsigned long int)P.x.c[0],
                        (unsigned long int)P.z.c[0],
                        (unsigned long int)Pd.x.c[0],
                        (unsigned long int)Pd.z.c[0],
                        ss);
                uart_puts(str);
#endif
                fp_cswap(&P.x, &Pd.x, ss);

                fp_cswap(&P.z, &Pd.z, ss);
#ifdef DBG
                sprintf(str,
                        "[DBG] Pre multiplication of P=(%lu, %lu) by cofactor=%lu on A=(%lu, %lu) ss=%d\n",
                        (unsigned long int)P.x.c[0],
                        (unsigned long int)P.z.c[0],
                        (unsigned long int)cof.c[0],
                        (unsigned long int)A.x.c[0],
                        (unsigned long int)A.z.c[0],
                        ss);
                uart_puts(str);
#endif
                // Create isogeny kernel K
                xMUL(&K, &A, &P, &cof);
#ifdef DBG
                sprintf(str,
                        "[DBG] Result K=(%ld, %ld)\n",
                        (unsigned long int)K.x.c[0],
                        (unsigned long int)K.z.c[0]);
                uart_puts(str);
#endif
                // Set the prime l, which means that the l-isogeny will be computed
                uint_set(&l, primes[i]);
#ifdef DBG
                sprintf(str,
                        "[DBG] Pre multiplication of Pd=(%lu, %lu) by l=%lu on A=(%lu, %lu)\n",
                        (unsigned long int)Pd.x.c[0],
                        (unsigned long int)Pd.z.c[0],
                        (unsigned long int)l.c[0],
                        (unsigned long int)A.x.c[0],
                        (unsigned long int)A.z.c[0]);
                uart_puts(str);
#endif
                xMUL(&Pd, &A, &Pd, &l);
#ifdef DBG
                sprintf(str,
                        "[DBG] Result Pd=(%ld, %ld)\n",
                        (unsigned long int)Pd.x.c[0],
                        (unsigned long int)Pd.z.c[0]);
                uart_puts(str);
#endif
                // We check if the action can be computed ?
                if (memcmp(&K.z, &fp_0, sizeof(fp)))
                { // depends only on randomness
                    if (i == last_iso[m])
                    {
#ifdef DBG
                        sprintf(str,
                                "[DBG] Computing lastxISOG A.x=%lu A.z=%lu l=%lu K.x=%lu K.z=%lu, sign=%d\n",
                                (long unsigned int)A.x.c[0],
                                (long unsigned int)A.z.c[0],
                                (long unsigned int)primes[i],
                                (long unsigned int)K.x.c[0],
                                (long unsigned int)K.z.c[0],
                                (uint8_t)s);
                        uart_puts(str);
#endif
                        lastxISOG(&A, &K, primes[i], b); // doesn't compute the images of points
#ifdef DBG
                        sprintf(str,
                                "[DBG] Result lastxISOG A.x=%lu A.z=%lu\n",
                                (long unsigned int)A.x.c[0],
                                (long unsigned int)A.z.c[0]);
                        uart_puts(str);
#endif
                    }
                    else
                    {
#ifdef DBG
                        sprintf(str,
                                "[DBG] Computing xISOG A.x=%lu A.z=%lu l=%lu K.x=%lu K.z=%lu P.x=%lu P.z=%lu Pd.x=%lu Pd.z=%lu sign=%d\n",
                                (long unsigned int)A.x.c[0],
                                (long unsigned int)A.z.c[0],
                                (long unsigned int)primes[i],
                                (long unsigned int)K.x.c[0],
                                (long unsigned int)K.z.c[0],
                                (long unsigned int)P.x.c[0],
                                (long unsigned int)P.z.c[0],
                                (long unsigned int)Pd.x.c[0],
                                (long unsigned int)Pd.z.c[0],
                                (uint8_t)s);
                        uart_puts(str);
#endif
#if defined(HAL) && defined(A2)
                        trigger_high();
#endif
                        xISOG(&A, &P, &Pd, &K, primes[i], b);
#if defined(HAL) && defined(A2)
                        // trigger_low();
#endif
#ifdef DBG
                        sprintf(str,
                                "[DBG] Result xISOG A.x=%lu A.z=%lu P.x=%lu P.z=%lu Pd.x=%lu Pd.z=%lu\n",
                                (long unsigned int)A.x.c[0],
                                (long unsigned int)A.z.c[0],
                                (long unsigned int)P.x.c[0],
                                (long unsigned int)P.z.c[0],
                                (long unsigned int)Pd.x.c[0],
                                (long unsigned int)Pd.z.c[0]);
                        uart_puts(str);
#endif
                    }

                    // With dummies we do e[i] = e[i] - (0 if e[i] == 0 else 1) + (0 if sign(e[i]) == 0 else 2)
                    // Which effectivelly does following
                    // if e[i] == 0              then e[i] = e[i]
                    // if e[i] != 0 and e[i] > 0 then e[i] = e[i] - 1
                    // if e[i] != 0 and e[i] < 0 then e[i] = e[i] + 1
                    //

                    e[i] = ec - (1 ^ b) + (s << 1);

                    counter[i]   = counter[i] - 1;
                    isog_counter = isog_counter + 1;
                }
            }

            if (counter[i] == 0)
            { // depends only on randomness
                finished[i] = true;
                uint_mul3_64(&k[m], &k[m], primes[i]);
            }
        }

        fp_inv(&A.z);
        fp_mul2(&A.x, &A.z);
        A.z   = fp_1;
        count = count + 1;
    }
    out->A = A.x;
#if defined(HAL) && defined(A1)
    trigger_low();
#endif
#ifdef DBG
    sprintf(str,
            "[DBG] END A.x=%lu A.z=%lu\n",
            (long unsigned int)A.x.c[0],
            (long unsigned int)A.z.c[0]

    );
    uart_puts(str);
#endif
    return 0;
}

/* includes public-key validation. */
bool csidh(public_key *out, public_key const *in, private_key const *priv,
           uint8_t const num_batches, int8_t const *max_exponent, unsigned int const num_isogenies, uint8_t const my)
{
    int8_t error;
    /*
        if (!validate(in)) {
                fp_random(&out->A);
                return false;
        }
    */
    error = action(out, in, priv, num_batches, max_exponent, num_isogenies, my);
    return error;
}
