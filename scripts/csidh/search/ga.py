# -*- coding: utf-8 -*-
# This code was taken and modified from the following source:
# https://github.com/geneticemfaults/geneticemfaults/
#
# The GA method with local search was presented in paper:
# Optimizing Electromagnetic Fault Injection with Genetic Algorithms
# https://repository.ubn.ru.nl/handle/2066/204497
from .unit import *
import logging
import numpy as np
from collections import OrderedDict
import random

P_MUT = 0.1
PUBLIC_EXPECTED = 0

cache = OrderedDict()


def generate_population(N):
    return [Unit() for i in range(N)]


def generate_population_custom(N, ext_offset_range):
    units = [Unit() for i in range(N)]
    i = 0
    ext_offset = 0
    while ext_offset < ext_offset_range and i < N:
        units[i].ext_offset = ext_offset
        ext_offset += ext_offset_range // N
        i += 1
    print([u.ext_offset for u in units])
    return units


def mutate_unit(solution, p_mut, Q=0.5):
    rand = random.random
    mut_and_clip = lambda x, _min, _max, _range: min(
        _max, max(_min, x + rand() * Q * _range - (Q * _range) / 2)
    )
    if rand() < p_mut:
        solution.ext_offset = int(
            round(
                mut_and_clip(
                    solution.ext_offset,
                    Unit.EXT_OFFSET_MIN,
                    Unit.EXT_OFFSET_MAX,
                    Unit.EXT_OFFSET_RANGE,
                )
            )
        )
    if rand() < p_mut:
        solution.width = mut_and_clip(
            solution.width, Unit.WIDTH_MIN, Unit.WIDTH_MAX, Unit.WIDTH_RANGE
        )
    if rand() < p_mut:
        solution.offset = mut_and_clip(
            solution.offset, Unit.OFFSET_MIN, Unit.OFFSET_MAX, Unit.OFFSET_RANGE
        )
    if rand() < p_mut and not Unit.is_husky:
        solution.offset_fine = int(
            round(
                mut_and_clip(
                    solution.offset_fine,
                    Unit.OFFSET_FINE_MIN,
                    Unit.OFFSET_FINE_MAX,
                    Unit.OFFSET_FINE_RANGE,
                )
            )
        )
    if rand() < p_mut and not Unit.is_husky:
        solution.width_fine = int(
            round(
                mut_and_clip(
                    solution.width_fine,
                    Unit.WIDTH_FINE_MIN,
                    Unit.WIDTH_FINE_MAX,
                    Unit.WIDTH_FINE_RANGE,
                )
            )
        )


def crossover(parent1, parent2):
    child = Unit()
    # o1 = min(parent1.ext_offset, parent2.ext_offset)
    # o2 = max(parent1.ext_offset, parent2.ext_offset)
    # child.ext_offset = random.choice(range(o1, o2 + 1))
    child.ext_offset = int(
        round(
            random.random() * (parent1.ext_offset - parent2.ext_offset)
            + parent2.ext_offset
        )
    )

    if child.ext_offset < Unit.EXT_OFFSET_MIN or child.ext_offset > Unit.EXT_OFFSET_MAX:
        child.ext_offset = random.randint(Unit.EXT_OFFSET_MIN, Unit.EXT_OFFSET_MAX)

    o1 = min(parent1.offset, parent2.offset)
    o2 = max(parent1.offset, parent2.offset)
    if Unit.is_husky:
        child.offset = random.choice(range(o1, o2 + 1))
    else:
        child.offset = random.uniform(o1, o2)
    # child.offset = random.random() * (parent1.offset - parent2.offset) + parent2.offset
    # if Unit.is_husky:
    #     child.offset = int(round(child.offset))

    o1 = min(parent1.width, parent2.width)
    o2 = max(parent1.width, parent2.width)
    if Unit.is_husky:
        child.width = random.choice(range(o1, o2 + 1))
    else:
        child.width = random.uniform(o1, o2)
    # child.width = random.random() * (parent1.width - parent2.width) + parent2.width
    # if Unit.is_husky:
    #    child.width = int(round(child.width))

    if not Unit.is_husky:
        o1 = min(parent1.width_fine, parent2.width_fine)
        o2 = max(parent1.width_fine, parent2.width_fine)
        child.width_fine = random.choice(range(o1, o2 + 1))

        o1 = min(parent1.offset_fine, parent2.offset_fine)
        o2 = max(parent1.offset_fine, parent2.offset_fine)
        child.offset_fine = random.choice(range(o1, o2 + 1))

    r1 = min(parent1.repeat, parent2.repeat)
    r2 = max(parent1.repeat, parent2.repeat)
    child.repeat = random.choice(range(r1, r2 + 1))

    return child


def selection_roulette(population, elite_size=1, mutate=mutate_unit):
    """Roulette selection with elitism"""
    N = len(population)
    newpop = []

    fits = np.array([float(u.fitness) for u in population])
    if fits.min() < 0:
        fits -= fits.min()
    fits /= fits.sum()

    parents1 = np.random.choice(population, size=N - elite_size, p=fits)
    parents2 = np.random.choice(population, size=N - elite_size, p=fits)
    for par1, par2 in zip(parents1, parents2):
        child = crossover(par1, par2)
        mutate(child, P_MUT)
        newpop += [child]

    newpop += sorted(population, reverse=True)[:elite_size]

    return newpop


def evaluate_unit_default(csidh, unit, num_measurements=3):
    """Evaluates a single unit"""
    if unit.is_husky:
        csidh.scope.glitch.width = int(unit.width)
        csidh.scope.glitch.offset = int(unit.offset)
        csidh.scope.glitch.repeat = int(unit.repeat)
        csidh.scope.glitch.ext_offset = int(unit.ext_offset)
    else:
        csidh.scope.glitch.width = unit.width
        csidh.scope.glitch.offset = unit.offset
        csidh.scope.glitch.repeat = unit.repeat
        csidh.scope.glitch.ext_offset = unit.ext_offset

    # Perform the measurements
    measurements = []
    responses = []

    for _ in range(num_measurements):
        csidh.reset_target()
        csidh.scope.arm()
        ret = csidh.action()
        if ret:
            logging.error("Timeout happened during acquisition")

        public_received = csidh.public_with_errors
        if not isinstance(public_received, int):
            measurements.append("RESET")
        elif public_received == PUBLIC_EXPECTED:
            measurements.append("NORMAL")
        else:
            measurements.append("JUSTRIGHT")
            responses.append(public_received)

    unit.width = csidh.scope.glitch.width  # CW rounds the values
    unit.offset = csidh.scope.glitch.offset
    unit.repeat = csidh.scope.glitch.repeat
    unit.measurements = measurements
    unit.responses = responses
    print(unit)
    print(unit.measurements)
    print(unit.responses)

    # Classify
    if not all(m == measurements[0] for m in measurements):
        unit.type = "CHANGING"
        N_normal = sum(1 for m in measurements if m == "NORMAL")
        N_reset = sum(1 for m in measurements if m == "RESET")
        N_justright = sum(1 for m in measurements if m == "JUSTRIGHT")
        unit.fitness = 4 + 1.2 * N_justright + 0.2 * N_normal + 0.5 * N_reset
    else:
        if measurements[0] == "NORMAL":
            unit.type = "NORMAL"
            unit.fitness = 2
        elif measurements[0] == "RESET":
            unit.type = "RESET"
            unit.fitness = 5
        elif measurements[0] == "JUSTRIGHT":
            unit.type = "JUSTRIGHT"
            unit.fitness = 10
    cache[unit] = unit.fitness


def evaluate_batch(csidh, population, evaluate_unit=evaluate_unit_default):

    uncached = [u for u in population if u not in cache]
    if not uncached:
        return [u.fitness for u in population]

    to_visit = np.array(uncached)

    for unit in population:
        if unit in cache:
            unit.fitness = cache[unit]

    for unit in to_visit:
        evaluate_unit(csidh, unit)

    return [u.fitness for u in population]
