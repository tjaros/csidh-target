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
PATH = "/home/attacker/Documents/tjaros/git/csidh-target/src/"
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


csidh.scope.vglitch_setup("both", default_setup=False)

# Voltage glitching
#

# Adc timeout
csidh.scope.adc.timeout = 5

# The fixed key for the attack.
key = [10, -10, 10]
attack = "attack2" if attack_type == "A2" else "attack1"
results_path = f"results-{key}-{attack}-{csidh.scope.clock.adc_src}.csv"
if os.path.exists(results_path):
    f = open(results_path, "a")
else:
    f = open(results_path, "w")
    f.write(
        "scope.glitch.width,scope.glitch.offset,scope.glitch.repeat,scope.glitch.ext_offset,good/bad/crash,public\n"
    )


stats = {"total": 0, "crash": 0, "good": 0, "bad": 0}


gc = cw.GlitchController(
    groups=["good", "bad", "crash"],
    parameters=["width", "offset", "repeat", "ext_offset"],
)


print(f"{csidh.scope.glitch.phase_shift_steps=}")
gc.set_global_step(1)

gc.set_range("width", 0, csidh.scope.glitch.phase_shift_steps // 2)
gc.set_step("width", csidh.scope.glitch.phase_shift_steps // 10 - 1)

gc.set_range("offset", 0, csidh.scope.glitch.phase_shift_steps // 2)
gc.set_step("offset", csidh.scope.glitch.phase_shift_steps // 10 - 1)

gc.set_range("repeat", 1, 8)

gc.set_range("ext_offset", 0, max_ext_offset)

ext_offset_step = max_ext_offset // 10
gc.set_step("ext_offset", ext_offset_step)

gc.widget_list_groups = None

init = 0

REPEATS = 10000
for _ in range(REPEATS):
    # width, offset, repeat, ext_offset = settings
    csidh.scope.glitch.width = random.randint(
        1500, csidh.scope.glitch.phase_shift_steps // 2
    )
    #csidh.scope.glitch.offset = random.randint(
    #    1500, csidh.scope.glitch.phase_shift_steps // 2
    #)
    #csidh.scope.glitch.repeat = random.randint(1, 15)
    #csidh.scope.glitch.width = 0
    csidh.scope.glitch.offset = 0
    #csidh.scope.glitch.repeat = random.randint(1, 60)
    #csidh.scope.glitch.ext_offset = sorted([random.randint(0, max_ext_offset), random.randint(1, max_ext_offset)])
    csidh.scope.glitch.ext_offset = 0

    actual = csidh.scope.adc.trig_count - init
    print(f"Actual: {actual}")

    init = csidh.scope.adc.trig_count
    csidh.reset_target()
    csidh.scope.arm()
    ret = csidh.action()
    if ret:
        print("Timeout happened during acquisition")
        continue

    public_received = csidh.public_with_errors
    if not isinstance(public_received, int):
        result = "crash"
        public_received = None
    elif public_received == public_expected:
        result = "good"
    else:
        result = "bad"
    stats[result] += 1

    line = f"{csidh.scope.glitch.width},{csidh.scope.glitch.offset},{csidh.scope.glitch.repeat},{csidh.scope.glitch.ext_offset},{result},{public_received}\n"
    f.write(line)

    print(stats)
    print(line)
    print(csidh.scope.glitch.output)
    f.flush()
f.close()
