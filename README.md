# PASM

Reorganization is being undergone.

Run tests with `coverage run pytest -q`. View coverate with `coverage report -m`. Type check with
`mypy binimage.py --strict`. File being developed with good coding principles is `binimage.py`.
File that has a lot of logic for ELF files is `pasm.py`. Currently, I'm trying to get the logic
for resolving jumps and internal links in the ELF file to a neat, simple representation.
