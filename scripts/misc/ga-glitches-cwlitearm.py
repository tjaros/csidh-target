from csidh import CSIDHCW as CSIDH
from csidh.search import *
import chipwhisperer as cw
import copy
import time
import os
import sys
import logging

from tqdm.notebook import trange
import random
import secrets

N_ITERS = 20
POPSIZE = 100

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, encoding="utf-8")

seed = random.randint(0, 2**32)
random.seed(seed)


def local_search(csidh, t1, t2, N_scanned):
    logger.info("Starting searches around JUSTRIGHTs")

    for u in [u for u in cache if u.type == "JUSTRIGHT"]:
        logger.info(f"{u}")
        for i in range(10):
            u = copy.deepcopy(u)
            mutate_unit(u, p_mut=1, Q=0.75)
            evaluate_unit(csidh, table, u)

    t2 = time.time()
    N_scanned.append(len(cache) - N_scanned[-1])
    print(
        "{}s elapsed, {}s in total\n{} scanned points".format(
            t2 - t1, t2 - t0, len(cache)
        )
    )
    print("Time elapsed local/total: {}/{} s".format(t2 - t1, t2 - t0))
    print("Scanned points local/total: {}/{}".format(N_scanned[1], sum(N_scanned)))
    print(" speed: {}s per point".format((t2 - t1) / N_scanned[-1]))

    print("Total speed: {}s per point".format((t2 - t0) / len(cache)))


def algo_search(csidh):
    """Parameter search using own algorithm"""

    population = generate_population_custom(POPSIZE, Unit.EXT_OFFSET_RANGE)
    N_scanned = []

    logger.info("Starting GA")
    t0 = tgen = time.time()
    for i in range(N_ITERS):
        logger.info("Iteration {}".format(i + 1))
        fits = evaluate_batch(csidh, population)
        population = selection_roulette(population, elite_size=3)
        logger.info(fits)
        logger.info("Mean={}, max={}".format(np.mean(fits), np.max(fits)))
        logger.info(
            "Iteration took {:.2f}s, total {:.2f}".format(
                time.time() - tgen, time.time() - t0
            )
        )
        tgen = time.time()

    t1 = time.time()
    N_scanned.append(len(cache))

    logger.info("Time elapsed GA/total: {}/{} s".format(t1 - t0, t1 - t0))
    logger.info("Scanned points GA/total: {}/{}".format(N_scanned[0], sum(N_scanned)))
    logger.info(" speed: {}s per point".format((t1 - t0) / N_scanned[-1]))

    write_cache_to_file("cache.json", cache, N_ITERS, POPSIZE, seed)


def main():
    logger.setLevel(logging.DEBUG)
    # Path to the CSIDH target source code
    PATH = "/home/attacker/Documents/tjaros/git/csidh-target/src"
    attack_type = "A1"

    # Initialize the CSIDH wrapper
    csidh = CSIDH(PATH, attack_type=attack_type)

    # Capture the first public key
    csidh.scope.arm()
    csidh.action()
    ret = csidh.scope.capture()
    if ret:
        logging.info("Timeout happened during acquisition")
    EXPECTED_PUBLIC = csidh.public_with_errors
    EXT_OFFSET_MAX = csidh.scope.adc.trig_count
    print(f"{EXPECTED_PUBLIC=}")
    print(f"{EXT_OFFSET_MAX=}")

    # Glitch setup
    # csidh.scope.glitch.enabled = True
    csidh.scope.glitch.clk_src = "clkgen"
    csidh.scope.glitch.output = "clock_xor"
    csidh.scope.glitch.trigger_src = "ext_continuous"
    csidh.scope.clock.adc_src = "clkgen_x4"
    # csidh.scope.glitch.num_glitches = 1
    # num_glitches = csidh.scope.glitch.num_glitches
    csidh.scope.io.hs2 = "glitch"
    Unit.is_husky = False

    # Adc timeout
    csidh.scope.adc.timeout = 5

    # Setup unit parameter ranges
    Unit.OFFSET_MIN = -44
    Unit.OFFSET_MAX = 44
    Unit.OFFSET_RANGE = Unit.OFFSET_MAX - Unit.OFFSET_MIN

    Unit.WIDTH_MIN = -44
    Unit.WIDTH_MAX = 44
    Unit.WIDTH_RANGE = Unit.WIDTH_MAX - Unit.WIDTH_MIN

    Unit.WIDTH_FINE_MIN = -255
    Unit.WIDTH_FINE_MAX = 255
    Unit.WIDTH_FINE_RANGE = Unit.WIDTH_FINE_MAX - Unit.WIDTH_FINE_MIN

    Unit.OFFSET_FINE_MIN = -255
    Unit.OFFSET_FINE_MAX = 255
    Unit.OFFSET_FINE_RANGE = Unit.OFFSET_FINE_MAX - Unit.OFFSET_FINE_MIN

    Unit.EXT_OFFSET_MIN = 0
    Unit.EXT_OFFSET_MAX = EXT_OFFSET_MAX
    Unit.EXT_OFFSET_RANGE = Unit.EXT_OFFSET_MAX

    Unit.REPEAT_MIN = 3
    Unit.REPEAT_MAX = 15
    Unit.repeat_range = Unit.REPEAT_MAX - Unit.REPEAT_MIN

    print("seed: {}".format(seed))
    algo_search(csidh)
    print("seed: {}".format(seed))


if __name__ == "__main__":
    main()
