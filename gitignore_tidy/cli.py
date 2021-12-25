import argparse
from gitignore_tidy.core import tidy
parser = argparse.ArgumentParser(description='Tidy up your .gitignore file')
parser.add_argument('--allow-trailing-whitespace', action=argparse.BooleanOptionalAction,
                    help='Whether or not to allow trailing whitespaces in file names')
args = parser.parse_args()
def main(allow_trailing_whitespace = args.allow_trailing_whitespace):
    tidy(allow_trailing_whitespace)
