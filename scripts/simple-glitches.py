from csidh import CSIDHCW as CSIDH
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
attack_type = "A2"

# Initialize the CSIDH wrapper
csidh = CSIDH(PATH, attack_type=attack_type)
cw.scope_logger.info("Scope setup done")

# Capture the first public key
csidh.scope.arm()
csidh.action()
ret = csidh.scope.capture()
if ret:
    print("Timeout happened during acquisition")
public_expected = csidh.public_with_errors
max_ext_offset = csidh.scope.adc.trig_count
print("Public key:", public_expected)
print("Max ext offset:", max_ext_offset)


# Glitch setup
csidh.scope.glitch.clk_src = "clkgen"
csidh.scope.glitch.output = "clock_xor"
csidh.scope.glitch.trigger_src = "ext_single"
csidh.scope.io.hs2 = "glitch"

# Adc timeout
csidh.scope.adc.timeout = 5

key = [10, -10, 10]
attack = "attack2" if attack_type == "A2" else "attack1"
results_path = f"results-{key}-{attack}.csv"

if os.path.exists(results_path):
    f = open(results_path, "a")
else:
    f = open(results_path, "w")
    f.write(
        "scope.glitch.width,scope.glitch.offset,scope.glitch.repeat,scope.glitch.ext_offset,good/bad/crash\n"
    )


stats = {"total": 0, "crash": 0, "good": 0, "bad": 0}

gc = cw.GlitchController(
    groups=["good", "bad", "crash"],
    parameters=["width", "offset", "repeat", "ext_offset"],
)

gc.set_global_step(1)
gc.set_range("width", 40, 48)
gc.set_range("offset", -15, 15)
gc.set_range("repeat", 8, 8)
gc.set_range("ext_offset", 1, max_ext_offset // 100)
gc.set_step("ext_offset", 100)
gc.widget_list_groups = None


for glitch_settings in gc.glitch_values():
    csidh.scope.glitch.width = glitch_settings[0]
    csidh.scope.glitch.offset = glitch_settings[1]
    csidh.scope.glitch.repeat = glitch_settings[2]
    csidh.scope.glitch.ext_offset = glitch_settings[3]

    # Reset and run the algorithm
    csidh.reset_target()
    csidh.scope.arm()
    ret = csidh.action()
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
    stats[result] += 1

    line = f"{csidh.scope.glitch.width},{csidh.scope.glitch.offset},{csidh.scope.glitch.repeat},{csidh.scope.glitch.ext_offset},{result}\n"
    f.write(line)

    print(stats)
    print(line)
    f.flush()
f.close()
