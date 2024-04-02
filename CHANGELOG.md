# Changelog

All changes we make to the assignment code or PDF will be documented in this file.

## [Unreleased] - yyyy-mm-dd

### Added

### Changed

### Fixed

## [0.1.1] - 2024-04-01

### Added

- code: add a note to README.md that pull requests and issues are welcome and
  encouraged.

### Changed

- handout: edit motivation for pre-tokenization to include a note about
  desired behavior with tokens that differ only in punctuation.
- handout: remove total number of points after each section.
- handout: mention that large language models (e.g., LLaMA and GPT-3) often use
  AdamW betas of (0.9, 0.95) (in contrast to the PyTorch defaults of (0.9, 0.999)).
- handout: explicitly mention the deliverable in the `adamw` problem.
- code: rename `test_serialization::test_checkpoint` to
  `test_serialization::test_checkpointing` to match the handout.
- code: slightly relax the time limit in `test_train_bpe_speed`.

### Fixed

- code: fix an issue in the `train_bpe` tests where the expected and vocab did
  not properly reflect tiebreaking with the lexicographically greatest pair.
  - This occurred because our reference implementation (which checks against HF)
    follows the GPT-2 tokenizer in remapping bytes that aren't human-readable to
    printable unicode strings. To match the HF code, we were erroneously tiebreaking
    on this remapped unicode representation instead of the original bytes.
- handout: fix the expected number of non-embedding parameters for model with
  recommended TinyStories hyperparameters (section 7.2).
- handout: replace `<|endofsequence|>` with `<|endoftext|>` in the `decoding` problem.
- code: fix the setup command (`pip install -e .'[test]'`)to improve zsh compatibility. 
- handout: fix various trivial typos and formatting errors.

## [0.1.0] - 2024-04-01

Initial release.