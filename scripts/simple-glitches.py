from csidh import CSIDH
import chipwhisperer as cw
import time
import os
import sys

from tqdm.notebook import trange
import random
import secrets

cw.scope_logger.setLevel(cw.logging.WARNING)


# Path to the CSIDH torget source code
PATH = "/home/tjaros/Documents/thesis/csidh-target/src/"

# Initialize the CSIDH wrapper
csidh = CSIDH(PATH)
csidh.setup()
csidh.flash_target()
csidh.reset_target()

# Capture the firs public key
csidh.scope.arm()
csidh.action()
ret = csidh.scope.capture()
if ret:
    print("Timeout happened during acquisition")

public_expected = csidh.public_with_errors
print(f"{public_expected=}")

max_ext_offset = csidh.scope.adc.trig_count

# Glitch setup
csidh.scope.glitch.clk_src = "clkgen"
csidh.scope.glitch.output = "clock_xor"
csidh.scope.glitch.trigger_src = "ext_single"
csidh.scope.io.hs2 = "glitch"

# Set seed
seed = 529357
random.seed(seed)


if os.path.exists("results.csv"):
    f = open("results-[10,-10,10].csv", "a")
else:
    f = open("results-[10,-10,10].csv", "w")
    f.write(
        "scope.glitch.width,scope.glitch.offset,scope.glitch.repeat,scope.glitch.ext_offset,good/bad/crash\n"
    )


stats = {"total": 0, "crash": 0, "good": 0, "bad": 0}

csidh.scope.adc.timeout = 5


while True:
    csidh.scope.glitch.ext_offset = random.randint(1, max_ext_offset)
    csidh.scope.glitch.width = random.randint(-49, 49)
    csidh.scope.glitch.offset = random.randint(-49, 49)
    for repeat in range(5, 12):
        csidh.scope.glitch.repeat = repeat
        # Reset and run the algorithm
        csidh.reset_target()
        csidh.scope.arm()
        csidh.action()
        ret = csidh.scope.capture()
        if ret:
            print("Timeout happened during acquisition")
            continue

        public_received = csidh.public_with_errors

        if not isinstance(public_received, int):
            result = "crash"
        elif public_received == public_expected:
            result = "good"
        else:
            result = "bad"

        stats["total"] += 1
        stats[result] += 1

        line = f"{csidh.scope.glitch.width},{csidh.scope.glitch.offset},{csidh.scope.glitch.repeat},{csidh.scope.glitch.ext_offset},{result}\n"
        f.write(line)

        print(line)
        print(stats)

        if stats["good"] + stats["bad"] == 10000:
            with open("stats-[10,-10,10]", "a") as g:
                print(stats, file=g)
            break
        f.flush()
f.close()
