import logging
import os
import struct
from typing import List, Optional
from abc import abstractmethod
import chipwhisperer as cw
from ctypes import *

import time


class CSIDHBase:
    SRC_PATH = "../../../src/"

    p = 419
    m = 10
    Fp_1 = 409

    @property
    @abstractmethod
    def public(self):
        pass

    @public.setter
    @abstractmethod
    def public(self, value: int):
        pass

    @property
    @abstractmethod
    def private(self):
        pass

    @private.setter
    @abstractmethod
    def private(self, value: List[int]):
        pass

    @abstractmethod
    def build_target(self):
        pass

    def from_projective(self, value: int) -> int:
        return (value * pow(self.Fp_1, -1, self.p)) % self.p

    def to_projective(self, value: int) -> int:
        return (value * self.Fp_1) % self.p


NUM_PRIMES = 3
MAX_EXPONENT = 10
LIMBS = 1


class UIntC(Structure):
    _fields_ = [("c", c_longlong * LIMBS)]


class Fp(Structure):
    _fields_ = [("c", c_longlong * LIMBS)]


class Proj(Structure):
    _fields_ = [("x", Fp), ("z", Fp)]


class PublicKey(Structure):
    _fields_ = [("A", Fp)]


class PrivateKey(Structure):
    _fields_ = [("e", c_ubyte * NUM_PRIMES)]


class CSIDHDLL(CSIDHBase):
    """Wrapper for CSIDH running locally on Linux"""

    DLL = "./libcsidh.so"

    def __init__(self, src_path="../../../src") -> None:
        self.SRC_PATH = src_path
        self.build_target()
        self.libcsidh = CDLL(self.DLL, mode=1)

        self._public = PublicKey()
        self._private = PrivateKey()

    def build_target(self):
        os.chdir(self.SRC_PATH)
        os.system("cmake -B build -S .")
        os.chdir("build")
        os.system("make")

    @property
    def public(self):
        return self._public.A.c[0]

    @public.setter
    def public(self, value: int):
        self._public.A.c[0] = value

    @property
    def private(self):
        return list(self._private.e)

    @private.setter
    def private(self, value: List[int]):
        for i in range(NUM_PRIMES):
            self._private.e[i] = -value[i]

    def action(self) -> int:
        """CSIDH Function

        :return bool: Success or error
        :param out: Public key
        :param in: Private key
        :param num_intervals: Always 1
        :param max_exponent: NUM_PRIMES * [MAX_EXPONENT]
        :param num_isogenies: NUM_PRIMES * MAX_EXPONENT
        :param my: Always 1
        """
        csidh = self.libcsidh.csidh
        csidh.argtypes = [
            POINTER(PublicKey),  # out
            POINTER(PublicKey),  # in
            POINTER(PrivateKey),  # priv
            c_ubyte,
            POINTER(NUM_PRIMES * c_byte),
            c_uint,
            c_ubyte,
        ]
        csidh.restype = c_bool

        result = PublicKey()

        max_exponent = (c_byte * NUM_PRIMES)()
        for i in range(NUM_PRIMES):
            max_exponent[i] = MAX_EXPONENT

        csidh(
            byref(result),
            byref(self._public),
            byref(self._private),
            1,
            byref(max_exponent),
            NUM_PRIMES * MAX_EXPONENT,
            1,
        )
        return result.A.c[0]


class CSIDHCW(CSIDHBase):
    """Wrapper for CSIDH running on Chipwhisperer"""




    def __init__(self, src_path="../../../src", attack_type="A1", PLATFORM="CW308_STM32F3") -> None:
        self.SCOPETYPE = "OPENADC"
        self.PLATFORM = PLATFORM
        self.SS_VER = "SS_VER_2_1"
        self.CRYPTO_TARGET = "NONE"
        self.BIN = "main-" + self.PLATFORM + ".hex"
        
        self.scope = None
        self.target = None
        self.programmer = None
        self.src_path  = src_path
        self.firmware_path = src_path + self.BIN
        self.attack_type = attack_type
        self.name=None

    def __str__(self) -> str:
        return f"Public:  {self.public}\nPrivate: {self.private}"
    
    def setup(self) -> None:
        self.connect()
        self.choose_programmer()
        time.sleep(0.05)
        self.scope.default_setup()
    
    def connect(self) -> None:
        try:
            if not self.scope.connectStatus:
                self.scope.con()
        except AttributeError:
            if self.name:
                self.scope = cw.scope(name=self.name)
            else:
                self.scope = cw.scope()

        try:
            if self.SS_VER == "SS_VER_2_1":
                self.target_type = cw.targets.SimpleSerial2
            elif self.SS_VER == "SS_VER_2_0":
                raise OSError("SS_VER_2_0 is deprecated. Use SS_VER_2_1")
            else:
                self.target_type = cw.targets.SimpleSerial
        except:
            self.SS_VER="SS_VER_1_1"
            self.target_type = cw.targets.SimpleSerial

        try:
            self.target = cw.target(self.scope, self.target_type)
        except:
            print("INFO: Caught exception on reconnecting to target - attempting to reconnect to scope first.")
            print("INFO: This is a work-around when USB has died without Python knowing. Ignore errors above this line.")
            self.scope = cw.scope()
            self.target = cw.target(self.scope, self.target_type)

        print("INFO: Found ChipWhisperer😍")


    def choose_programmer(self) -> None:
        if "STM" in self.PLATFORM or self.PLATFORM == "CWLITEARM" or self.PLATFORM == "CWNANO":
            self.programmer = cw.programmers.STM32FProgrammer
        elif self.PLATFORM == "CW303" or self.PLATFORM == "CWLITEXMEGA":
            self.programmer = cw.programmers.XMEGAProgrammer
        elif "neorv32" in self.PLATFORM.lower():
            self.programmer = cw.programmers.NEORV32Programmer
        elif self.PLATFORM == "CW308_SAM4S" or self.PLATFORM == "CWHUSKY":
            self.programmer = cw.programmers.SAM4SProgrammer
        else:
            self.programmer = None

    def setup_(self) -> None:
        """Set up the scope, target, and programmer"""
        self.scope.gain.db = 25
        self.scope.adc.samples = 24000
        self.scope.adc.offset = 0
        self.scope.adc.decimate = 200
        self.scope.adc.basic_mode = "rising_edge"
        self.scope.adc.timeout = 5
        self.scope.clock.clkgen_freq = 7370000
        #self.scope.clock.adc_src = "clkgen_x4"
        self.scope.trigger.triggers = "tio4"
        self.scope.io.tio1 = "serial_rx"
        self.scope.io.tio2 = "serial_tx"
        # self.scope.io.hs2 = "clkgen"

    def voltage_glitching_setup(self) -> None:
        if self.scope._is_husky:
            self.scope.glitch.enabled = True
            self.scope.glitch.clk_src = "pll"
            self.scope.io.glitch_hp = False
            self.scope.io.glitch_hp = True
            self.scope.io.glitch_lp = False
            self.scope.io.glitch_lp = False
        else:
            self.scope.glitch.clk_src = "clkgen" # set glitch input clock
        self.scope.glitch.output = "glitch_only" # glitch_out = clk ^ glitch
        self.scope.glitch.trigger_src = "ext_single" # glitch only after scope.arm() called
        if self.PLATFORM == "CWLITEXMEGA":
            self.scope.io.glitch_lp = True
            self.scope.io.glitch_hp = True
        elif self.PLATFORM == "CWLITEARM":
            self.scope.io.glitch_lp = True
            self.scope.io.glitch_hp = True
        elif self.PLATFORM == "CW308_STM32F3":
            self.scope.io.glitch_hp = True
            self.scope.io.glitch_lp = True

    def build_target(self) -> None:
        """Builds the target using make"""
        os.chdir(self.src_path)
        os.system(
            f"make clean PLATFORM={self.PLATFORM} CRYPTO_TARGET={self.CRYPTO_TARGET} SS_VER={self.SS_VER} ATTACK_TYPE={self.attack_type}"
        )
        os.system(
            f"make PLATFORM={self.PLATFORM} CRYPTO_TARGET={self.CRYPTO_TARGET} SS_VER={self.SS_VER} ATTACK_TYPE={self.attack_type}"
        )

    def program_target(self) -> None:
        cw.program_target(self.scope, self.programmer, self.firmware_path)
        if self.SS_VER == "SS_VER_2_1":
            self.target.reset_comms()

    def reset_target(self)-> None:
        if self.PLATFORM == "CW303" or self.PLATFORM == "CWLITEXMEGA":
            self.scope.io.pdic = 'low'
            time.sleep(0.1)
            self.scope.io.pdic = 'high_z' #XMEGA doesn't like pdic driven high
            time.sleep(0.1) #xmega needs more startup time
        elif "neorv32" in self.PLATFORM.lower():
            raise IOError("Default iCE40 neorv32 build does not have external reset - reprogram device to reset")
        elif self.PLATFORM == "CW308_SAM4S" or self.PLATFORM == "CWHUSKY":
            self.scope.io.nrst = 'low'
            time.sleep(0.25)
            self.scope.io.nrst = 'high_z'
            time.sleep(0.25)
        else:  
            self.scope.io.nrst = 'low'
            time.sleep(0.05)
            self.scope.io.nrst = 'high_z'
            time.sleep(0.05)
        self.target.flush()

    def reset_target_(self) -> None:
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

    def dis(self) -> None:
        self.target.dis()
        self.scope.dis()


if __name__ == "__main__":
    import sys

    argv = sys.argv
    if len(argv) < 2:
        print("USAGE: {argv[0]} CW|DLL")
        sys.exit(1)
    if argv[1] == "CW":
        csidh = CSIDHCW()
        csidh.action()
        print(csidh.public)
        print(csidh.private)
    elif argv[1] == "DLL":
        csidh = CSIDHDLL()
        print(csidh.csidh(0, [-10, 10, -10]))
