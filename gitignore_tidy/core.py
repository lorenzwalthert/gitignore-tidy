import logging
import os
import re
import sys
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.INFO)


def tidy(files, allow_trailing_whitespace=False):
    [tidy_one(file, allow_trailing_whitespace) for file in files]


def tidy_one(file, allow_trailing_whitespace):
    if not os.path.exists(file):
        raise FileNotFoundError(f'{file} not found.')

    with open(file) as f:
        lines = _normalize(
            f.read().splitlines(),
            allow_trailing_whitespace=allow_trailing_whitespace,
        )

    if len(lines) < 1:
        logger.info(f'{file} is empty.')
        return

    sorted_lines = _sort_lines(lines)
    if sorted_lines == lines:
        logger.info(f'{file} already tidy.')
        return

    with open(file, 'w') as f:
        f.writelines([line + '\n' for line in sorted_lines])
    logger.info(f'Succesfully written {file}.')


def _normalize(lines, allow_trailing_whitespace):
    if not allow_trailing_whitespace:
        lines = [re.sub('^(!)? *\t*', '\\1', line) for line in lines]
    lines = [re.sub(' *\t*$', '', line) for line in lines]
    unique = []
    for line in lines:
        if line not in unique:
            unique.append(line)
    return unique


def _sort_lines(lines):
    original = lines
    non_negated = [re.sub('^!', '', line) for line in lines]
    sorted_non_negated = sorted(non_negated)
    sorted_negated = []
    for line in sorted_non_negated:
        negated_cand = ('!' + line)
        if negated_cand in original:
            sorted_negated.append(negated_cand)
        else:
            sorted_negated.append(line)

    return sorted_negated


def order(seq):
    return [x for x, y in sorted(enumerate(seq), key=lambda x: x[1])]
