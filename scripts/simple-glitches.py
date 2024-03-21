from csidh import CSIDH
import chipwhisperer as cw
import time

from tqdm.notebook import trange
import random

PATH = '/home/tjaros/Documents/thesis/csidh-target/src/'
csidh = CSIDH(PATH)

csidh.setup()

csidh.flash_target()

cw.scope_logger.setLevel(cw.logging.WARNING)


csidh.scope.clock.adc_src = 'clkgen_x1'
csidh.reset_target()
csidh.scope.clock

csidh.reset_target()
csidh.action()
csidh.scope.arm()
csidh.action()
ret = csidh.scope.capture()
if ret:
    print("Timeout happened during acquisition")

public_correct = csidh.public_with_errors
print(public_correct)

print(csidh.scope.adc.trig_count)

csidh.scope.glitch.clk_src = 'clkgen'
csidh.scope.glitch.output = "clock_xor"
csidh.scope.glitch.trigger_src = "ext_single"
csidh.scope.io.hs2 = "glitch"
csidh.scope.glitch


results = []

seed = random.randint(1, 1000000)
random.seed(seed)

f = open(f"glitches-{seed}.csv", "w")
print(f"glitches-{seed}.csv")
f.write('"scope.glitch.width", "scope.glitch.offset", "scope.glitch.repeat", "scope.glitch.ext_offset", "good/bad/crash"\n')
f.flush()

while True:
    csidh.scope.adc.timeout = 5
    csidh.scope.glitch.repeat = random.randint(1, 6)
    csidh.scope.glitch.width = random.randint(-49, 50)
    csidh.scope.glitch.offset = random.randint(-49, 50)
    csidh.scope.glitch.ext_offset = random.randint(1, 1690000)
    csidh.reset_target()
    #csidh.public  = 0
    #csidh.private = [9, 0, 0]
    csidh.scope.arm()
    csidh.action()
    ret = csidh.scope.capture()
    if ret:
        print("Timeout happened during acquisition")
        continue

    public_received = csidh.public_with_errors
    
    if not isinstance(public_received, int):
        result = "crash"
    else:
        result = "good" if public_received == public_correct else "bad"
    

    f.write(
        f"{csidh.scope.glitch.width},{csidh.scope.glitch.offset},{csidh.scope.glitch.repeat},{csidh.scope.glitch.ext_offset},{result}\n"
    )
    f.flush()
f.close()
