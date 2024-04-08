import logging
import os
import struct
from typing import List, Optional
import chipwhisperer as cw

import time


class CSIDH:
    """Wrapper for CSIDH running on Chipwhisperer"""

    SCOPETYPE = "OPENADC"
    PLATFORM = "CWLITEARM"
    SS_VER = "SS_VER_2_1"
    CRYPTO_TARGET = "NONE"
    BIN = "main-" + PLATFORM + ".hex"
    p = 419
    m = 10

    def __init__(self, src_path="../src") -> None:
        self.scope: Optional[cw.scopes.OpenADC] = None
        self.target: Optional[cw.targets.SimpleSerial2] = None
        self.programmer = cw.programmers.STM32FProgrammer
        self.src_path: str = src_path
        self.firmware_path: str = src_path + self.BIN

    def __str__(self) -> str:
        return f"Public:  {self.public}\nPrivate: {self.private}"

    def setup(self) -> None:
        """Set up the scope, target, and programmer"""
        self.scope = cw.scope()
        self.scope.default_setup()
        self.target = cw.target(self.scope, cw.targets.SimpleSerial2, flush_on_err=True)
        self.scope.gain.db = 25
        self.scope.adc.samples = 24000
        self.scope.adc.offset = 0
        self.scope.adc.decimate = 200
        self.scope.adc.basic_mode = "rising_edge"
        self.scope.adc.timeout = 5
        self.scope.clock.clkgen_freq = 7370000
        self.scope.clock.adc_src = "clkgen_x1"
        self.scope.trigger.triggers = "tio4"
        self.scope.io.tio1 = "serial_rx"
        self.scope.io.tio2 = "serial_tx"
        # self.scope.io.hs2 = "clkgen"

    def build_target(self) -> None:
        """Builds the target using make"""
        os.chdir(self.src_path)
        os.system(
            "make clean PLATFORM={self.PLATFORM} CRYPTO_TARGET={self.CRYPTO_TARGET} SS_VER={self.SS_VER}"
        )
        os.system(
            f"make PLATFORM={self.PLATFORM} CRYPTO_TARGET={self.CRYPTO_TARGET} SS_VER={self.SS_VER}"
        )

    def program_target(self) -> None:
        cw.program_target(self.scope, self.programmer, self.firmware_path)
        if self.SS_VER == "SS_VER_2_1":
            self.target.reset_comms()

    def reset_target(self) -> None:
        self.scope.io.nrst = "low"
        time.sleep(0.05)
        self.scope.io.nrst = "high"
        time.sleep(0.05)
        self.target.flush()

    def flash_target(self) -> None:
        self.build_target()
        self.program_target()
        self.reset_target()

    @property
    def public_with_errors(self):
        self.target.flush()
        self.target.send_cmd("2", 0, bytearray([]))
        value = self.target.simpleserial_read_witherrors(timeout=100, glitch_timeout=1)
        logging.info(f"CSIDH:public: {value=}")
        if not value["valid"]:
            return value
        value = int.from_bytes(value["payload"], "little")
        self.target.flush()
        return (value * pow(409, -1, 419)) % 419

    @property
    def public(self):
        self.target.flush()
        self.target.send_cmd("2", 0, bytearray([]))
        value = self.target.simpleserial_read(timeout=10)
        value = int.from_bytes(value, "little")
        self.target.flush()
        return (value * pow(409, -1, 419)) % 419

    @public.setter
    def public(self, value: int):
        self.target.flush()
        self.target.send_cmd("1", 0, value.to_bytes(8, "little"))
        self.target.flush()
        time.sleep(0.1)

    @property
    def private(self):
        self.target.flush()
        self.target.send_cmd("4", 0, bytearray([]))
        time.sleep(0.1)
        value = self.target.simpleserial_read()
        self.target.flush()
        time.sleep(0.1)
        return list([-struct.unpack("b", bytearray([x]))[0] for x in value])

    @private.setter
    def private(self, value: List[int]):
        assert len(value) == 3
        self.target.flush()
        priv = b""
        for x in value:
            priv += struct.pack("b", -x)
        self.target.send_cmd("3", 0, priv)
        time.sleep(0.1)

    def action(self) -> int:
        self.target.send_cmd("5", 0, bytearray([]))
        time.sleep(0.4)


if __name__ == "__main__":
    PATH = "../src/"
    csidh = CSIDH(PATH)
    csidh.setup()
    csidh.flash_target()
    csidh.reset_target()
    csidh.action()
    print(csidh.public)
    print(csidh.private)
