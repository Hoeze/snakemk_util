# Changelog

## [3.0.1](https://github.com/Hoeze/snakemk_util/compare/v3.0.0...v3.0.1) (2026-05-09)


### Miscellaneous Chores

* trigger v3.0.1 release ([340bc21](https://github.com/Hoeze/snakemk_util/commit/340bc210e0827225e6f0d6ca67309a279a06415e))

## [3.0.0](https://github.com/Hoeze/snakemk_util/compare/v2.0.2...v3.0.0) (2026-05-09)


### ⚠ BREAKING CHANGES

* **cli:** `--wildcards` no longer accepts a single comma-separated string. Callers must pass each pair as its own argv token, e.g. `--wildcards k1=v1 k2=v2` instead of `--wildcards "k1=v1,k2=v2"`. A legacy comma-separated string is now silently interpreted as a single value containing commas, since the new contract allows commas in values.

### Features

* **cli:** take --wildcards as repeated key=value tokens ([#13](https://github.com/Hoeze/snakemk_util/issues/13)) ([41afc05](https://github.com/Hoeze/snakemk_util/commit/41afc054c853cc3ff78bd4d846b0a2616d0a6f14))


### Bug Fixes

* address review findings across CLI, types, formatting, and R docs ([#11](https://github.com/Hoeze/snakemk_util/issues/11)) ([8f2ed20](https://github.com/Hoeze/snakemk_util/commit/8f2ed20bcfe983101bba5fa613e81b94e937f565))

## [2.0.2](https://github.com/Hoeze/snakemk_util/compare/v2.0.1...v2.0.2) (2026-05-08)


### Miscellaneous Chores

* trigger v2.0.2 release ([1e52612](https://github.com/Hoeze/snakemk_util/commit/1e52612cbdb7ae4f5330c3f77cc99c0537570863))

## [2.0.1](https://github.com/Hoeze/snakemk_util/compare/v2.0.0...v2.0.1) (2026-05-08)


### Bug Fixes

* preserve named params when loading rule args ([8c4641c](https://github.com/Hoeze/snakemk_util/commit/8c4641c0752e0c2eec491af6786b7ad073e07bcf))
* **release-please:** drop invalid $schema key from manifest ([697b84e](https://github.com/Hoeze/snakemk_util/commit/697b84ea1fa15bc1b4cab0180b4fb38c7b64b2ae))
