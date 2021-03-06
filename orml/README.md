# open-runtime-module-library

[![Crates.io](https://img.shields.io/crates/v/orml-tokens)](https://crates.io/search?q=orml)
[![GitHub](https://img.shields.io/github/license/open-web3-stack/open-runtime-module-library)](https://github.com/open-web3-stack/open-runtime-module-library/blob/master/LICENSE)

The Open Runtime Module Library (ORML) is a community maintained collection of Substrate runtime modules.

## Runtime Modules Overview

- [orml-traits](./traits)
    - Shared traits including `BasicCurrency`, `MultiCurrency`, `Auction` and more.
- [orml-utilities](./utilities)
	- Various utilities including `OrderSet`.
- [orml-tokens](./tokens)
    - Fungible tokens module that implements `MultiCurrency` trait.
- [orml-currencies](./currencies)
	- Provide `MultiCurrency` implementation using `pallet-balances` and `orml-tokens` module.
- [orml-oracle](./oracle)
    - Oracle module that makes off-chain data available on-chain.
- [orml-auction](./auction)
	- Auction module that implements `Auction` trait.
- [orml-vesting](./vesting)
    - Provides scheduled balance locking mechanism, in a *graded vesting* way.
- [orml-gradually-update](./gradually-update)
    - Provides way to adjust numeric parameter gradually over a period of time.

## Example

Checkout [orml-workshop](https://github.com/xlc/orml-workshop) for example usage.

## Development

### Makefile targets

- `make check`
	- Type check the code, without std feature, excluding tests.
- `make check-tests`
	- Type check the code, with std feature, including tests.
- `make test`
	- Run tests.

### `Cargo.toml`

ORML use `Cargo.dev.toml` to avoid workspace conflicts with project cargo config. To use cargo commands in ORML workspace, create `Cargo.toml` by running

- `cp Cargo.dev.toml Cargo.toml`, or
- `make Cargo.toml`, or
- change the command to `make dev-check` etc which does the copy. (For the full list of `make` commands, check `Makefile`)
