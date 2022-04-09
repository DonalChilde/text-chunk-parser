# Development TODOs

## Before next release

## Cli example

- Testing
  - cmd line tests
  - test resources
- Click
  - bash completion
  - modular click layout
  - std in/std out
  - error handling
  - ctx.obj
  - verbose output
  - progress bar
- Optional Rich output
  - optional imports
- PyPi packging
- Read the docs
  - Sphinx
  - check out cc for doc format examples
  - make modular docs, so its easy to remove example code
  - doc all the places to remove example code
  - improve dev setup docs with material from cc
- Git
  - git hooks
  - git badges
- App
  - Configuration
    - app config
      - env variables
    - app data directory
  - file info
    - returns a dict of file info.
  - file hashes
    - hash factory to calculate multiple hashes with one disk read.
- file info, hash app
  - support multiple simultainious hashes.
  - output to std out
  - output dict or csv list
  - patternmatching input option, requires dir for input.
  - compare known hashes to files?
