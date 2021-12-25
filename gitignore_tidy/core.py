import os 
PATH_GITIGNORE = ".gitignore"
import logging
import sys
import re 

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.INFO)

def tidy():
    if not os.path.exists(PATH_GITIGNORE):
        raise FileNotFoundError("No .gitignore file present.")

    with open(PATH_GITIGNORE, 'r') as f:
        lines = _normalize(f.read().splitlines())
    
    if len(lines) < 1:
        logger.info(f"{PATH_GITIGNORE} is empty.")
        return 

    sorted_lines = _sort_lines(lines)
    if sorted_lines == lines:
        logger.info(f"{PATH_GITIGNORE} already tidy.")
        return

    with open(PATH_GITIGNORE, 'w') as f:
        f.writelines([line + "\n" for line in sorted_lines])
    logger.info(f"Succesfully written f{PATH_GITIGNORE}.")

def _normalize(lines):
    lines = [re.sub("^(!)? *\t*", "\\1", line) for line in lines]
    lines = [re.sub(" *\t*$", "", line) for line in lines]
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
        negated_cand = ("!" + line)
        if negated_cand in original:
            sorted_negated.append(negated_cand)
        else:
            sorted_negated.append(line)
    
    return sorted_negated

def order(seq): 
    return [x for x, y in sorted(enumerate(seq), key=lambda x: x[1])]

if __name__ == "__main__":
    tidy()


