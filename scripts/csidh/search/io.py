from .unit import Unit
from collections import OrderedDict
import json


def write_cache_to_file(filename, cache, iterations="", population_size="", seed=""):
    result = {}
    result["iterations"] = iterations
    result["population_size"] = population_size
    result["seed"] = seed

    measurements = []
    for i, unit in enumerate(cache):
        entry = {}
        entry["index"] = i
        entry["unit"] = repr(unit)
        entry["responses"] = unit.responses
        entry["measurements"] = unit.measurements
        measurements.append(entry)
    result["measurements"] = measurements

    with open(filename, "w") as f:
        json.dump(result, f)
