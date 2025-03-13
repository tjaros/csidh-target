# -*- coding: utf-8 -*-
# This code was taken and modified from the following source:
# https://github.com/geneticemfaults/geneticemfaults/
#
# The GA method with local search was presented in paper:
# Optimizing Electromagnetic Fault Injection with Genetic Algorithms
# https://repository.ubn.ru.nl/handle/2066/204497


import random


class Unit:
    is_husky = True

    OFFSET_MIN = None
    OFFSET_MAX = None
    OFFSET_RANGE = None

    WIDTH_MIN = None
    WIDTH_MAX = None
    WIDTH_RANGE = None

    OFFSET_FINE_MIN = None
    OFFSET_FINE_MAX = None
    OFFSET_FINE_RANGE = None

    WIDTH_FINE_MIN = None
    WIDTH_FINE_MAX = None
    WIDTH_FINE_RANGE = None

    REPEAT_MIN = None
    REPEAT_MAX = None
    REPEAT_RANGE = None

    EXT_OFFSET_MIN = None
    EXT_OFFSET_MAX = None
    EXT_OFFSET_RANGE = None

    def __init__(self, repr=None):
        measurements = []
        responses = []
        self.offset_fine = None
        self.width_fine = None
        if not repr:
            self.ext_offset = random.randint(self.EXT_OFFSET_MIN, self.EXT_OFFSET_MAX)
            self.offset = (
                random.randint(self.OFFSET_MIN, self.OFFSET_MAX)
                if self.is_husky
                else random.uniform(self.OFFSET_MIN, self.OFFSET_MAX)
            )
            self.width = (
                random.randint(self.WIDTH_MIN, self.WIDTH_MAX)
                if self.is_husky
                else random.uniform(self.WIDTH_MIN, self.WIDTH_MAX)
            )
            self.repeat = random.randint(self.REPEAT_MIN, self.REPEAT_MAX)
            if not self.is_husky:
                self.offset_fine = random.randint(
                    self.OFFSET_FINE_MIN, self.OFFSET_FINE_MAX
                )
                self.width_fine = random.randint(
                    self.WIDTH_FINE_MIN, self.WIDTH_FINE_MAX
                )

            self.fitness = None
            self.type = None
        else:
            repr = repr.split(",")
            self.ext_offset = int(repr[0])
            self.offset = int(float(repr[1])) if self.is_husky else float(repr[1])
            self.width = int(float(repr[2])) if self.is_husky else float(repr[2])
            self.repeat = int(float(repr[3]))
            self.type = repr[4]
            if not self.is_husky:
                self.offset_fine = int(repr[5])
                self.width_fine = int(repr[6])

            if (
                self.is_husky
                and len(repr) == 6
                or (not self.is_husky and len(repr) == 8)
            ):
                value = repr[-1]

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
        result = "{:d},{:f},{:f},{:d},{},{}".format(
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
                self.ext_offset,
                self.offset,
                self.width,
                self.repeat,
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
