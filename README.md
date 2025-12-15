# csidh-target

This repository contains sources for CSIDH implementation taken from [csidhfi](https://github.com/csidhfi/csidhfi/tree/master).

## Important 

The folder `./src/hal` needs to be symlinked to `../chipwhisperer/hardware/victims/firmware/hal`

## Branches

Individual CSIDH implementations are available in separate branches:

- `dummy` - Implementation with dummy operations
- `dummy-free` - Implementation without dummy operations

To switch between implementations:

```bash
git switch dummy
```

or

```bash
git switch dummy-free
```

## Credits

[csidhfi](https://github.com/csidhfi/csidhfi/tree/master)
