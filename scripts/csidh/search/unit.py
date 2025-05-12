# -*- coding: utf-8 -*-
# This code was taken and modified from the following source:
# https://github.com/geneticemfaults/geneticemfaults/
#
# The GA method with local search was presented in paper:
# Optimizing Electromagnetic Fault Injection with Genetic Algorithms
# https://repository.ubn.ru.nl/handle/2066/204497


import random
import json
import re
import ast


class Unit:
    is_husky = True

    OFFSET_MIN = 0
    OFFSET_MAX = 0
    OFFSET_RANGE = 0

    WIDTH_MIN = 0
    WIDTH_MAX = 0
    WIDTH_RANGE = 0

    OFFSET_FINE_MIN = 0
    OFFSET_FINE_MAX = 0
    OFFSET_FINE_RANGE = 0

    WIDTH_FINE_MIN = 0
    WIDTH_FINE_MAX = 0
    WIDTH_FINE_RANGE = 0

    REPEAT_MIN = 0
    REPEAT_MAX = 0
    REPEAT_RANGE = 0

    EXT_OFFSET_MIN = 0
    EXT_OFFSET_MAX = 0
    EXT_OFFSET_RANGE = 0

    def __init__(self, repr=None, parser=None, num_glitches=1):
        self.measurements = []
        self.responses = []
        self.offset_fine = None
        self.width_fine = None
        self.ext_offset = None
        self.offset = None
        self.width = None
        self.repeat = None
        self.num_glitches = num_glitches
        self.fitness = None
        self.type = None

        if parser:
            parser = self.parser
        else:
            parser = self.old_parser
        

        if not repr:
            self.generate_unit()
        else:
            parser(repr)

    def generate_unit(self):
        rand_ext_offset = lambda: random.randint(self.EXT_OFFSET_MIN, self.EXT_OFFSET_MAX)
        self.ext_offset = rand_ext_offset()
        if self.num_glitches != 1:
            self.ext_offset = [ rand_ext_offset() for _ in range(self.num_glitches)]

        rand_ow = random.randint if self.is_husky else random.uniform  
        self.offset = rand_ow(self.OFFSET_MIN, self.OFFSET_MAX)
        self.width = rand_ow(self.WIDTH_MIN, self.WIDTH_MAX)

        rand_repeat = lambda : random.randint(self.REPEAT_MIN, self.REPEAT_MAX)
        self.repeat = rand_repeat()
        if self.num_glitches != 1:
            self.ext_offset = [ rand_repeat() for _ in range(self.num_glitches)]

        
        if not self.is_husky:
            self.offset_fine = random.randint(
                self.OFFSET_FINE_MIN, self.OFFSET_FINE_MAX
            )
            self.width_fine = random.randint(
                self.WIDTH_FINE_MIN, self.WIDTH_FINE_MAX
            )


    def parser(self,data):
        pattern = r"^\[?(\d+)(?:,\s*(\d+))?\]?,([\d.]+),([\d.]+),(\[.*?\]|\d+),(\w+),([\d.]+)$"
        match = re.match(pattern, data)
        if match:
            groups = match.groups()
            first_number = int(groups[0])
            second_number = int(groups[1]) if groups[1] else None

            if second_number:
                self.ext_offset = [first_number, second_number]
            else:
                self.ext_offset = first_number

            self.offset = float(groups[2])
            self.width  = float(groups[3])
            list_or_number = ast.literal_eval(groups[4]) if groups[4].startswith("[") else int(groups[4])
            self.repeat = list_or_number
            self.type = groups[5]
            self.fitness = float(groups[6])
    
    def old_parser(self, data):
        data = data.split(",")
        self.ext_offset = int(data[0])
        self.offset = int(float(data[1])) if self.is_husky else float(data[1])
        self.width = int(float(data[2])) if self.is_husky else float(data[2])
        self.repeat = int(float(data[3]))
        self.type = data[4]
        if not self.is_husky:
            self.offset_fine = int(data[5])
            self.width_fine = int(data[6])

        if (
            self.is_husky
            and len(data) == 6
            or (not self.is_husky and len(data) == 8)
        ):
            value = data[-1]

            if value == "None":
                self.fitness = None
            else:
                self.fitness = float(value)
            

    def __dict__(self):
        return {
            'ext_offset':self.ext_offset,
            'offset':self.offset,
            'width':self.width,
            'repeat':self.repeat,
            'type':self.type,
            'fitness':self.fitness,
            'offset_fine':self.offset_fine,
            'width_fine':self.width_fine
        }


    def __str__(self):
        result =  f"(ext_offset={self.ext_offset}, offset={self.offset}, width={self.width}, repeat={self.repeat}, type={self.type}, fitness={self.fitness}"
        if not self.is_husky:
            result += f" offset_fine={self.offset_fine}, width_fine={self.width_fine}"
        return result + ")"

    def __repr__(self):
        result = "{},{:f},{:f},{},{},{}".format(
            self.ext_offset,
            self.offset,
            self.width,
            self.repeat,
            self.type,
            self.fitness
        )
        if not self.is_husky:
            result += ",{:d},{:d}".format(
                self.offset_fine,
                self.width_fine,
            )
        return result

    def __lt__(self, other):
        return self.fitness < other.fitness

    def __eq__(self, other):
        return (
            self.ext_offset == other.ext_offset
            and self.offset == other.offset
            and self.width == other.width
            and self.repeat == other.repeat
        ) and (True if self.is_husky else 
               self.offset_fine == other.offset_fine
               and self.width_fine == other.width_fine)

    def __hash__(self):
        if self.is_husky:
            return hash(
            (
                self.ext_offset if not isinstance(self.ext_offset, list) else tuple(self.ext_offset),
                self.offset,
                self.width,
                self.repeat if not isinstance(self.repeat, list) else tuple(self.repeat),
            )
        )
        return hash(
            (
                self.ext_offset,
                self.offset,
                self.width,
                self.repeat,
                self.offset_fine,
                self.width_fine,
            )
        )

    def distance_to(self, point):
        assert type(point) is type(self), "Cannot compare to another type!"
        if self.is_husky:
            return (
                ((point.ext_offset - self.ext_offset) / self.EXT_OFFSET_RANGE) ** 2
                + ((point.offset - self.offset) / self.OFFSET_RANGE) ** 2
                + ((point.width - self.width) / self.WIDTH_RANGE) ** 2
                # + ((point.repeat - self.repeat) / REPEAT_RANGE) ** 2
            ) ** 0.5
        else:
            return (
                ((point.ext_offset - self.ext_offset) / self.EXT_OFFSET_RANGE) ** 2
                + ((point.offset - self.offset) / self.OFFSET_RANGE) ** 2
                + ((point.width - self.width) / self.WIDTH_RANGE) ** 2
                + ((point.offset_fine - self.offset_fine) / self.OFFSET_FINE_RANGE) ** 2
                + ((point.width_fine - self.width_fine) / self.WIDTH_FINE_RANGE) ** 2
                # + ((point.repeat - self.repeat) / REPEAT_RANGE) ** 2
            ) ** 0.5
