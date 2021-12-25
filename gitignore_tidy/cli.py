import argparse

from gitignore_tidy.core import tidy
PATH_GITIGNORE = '.gitignore'

parser = argparse.ArgumentParser(description='Tidy up your .gitignore file')
parser.add_argument(
    '--allow-trailing-whitespace', action=argparse.BooleanOptionalAction,
    help='Whether or not to allow trailing whitespaces in file names',
)
parser.add_argument(
    'files', type=str, nargs='*',
    default=[PATH_GITIGNORE], help='files to tidy',
)
args = parser.parse_args()


def main(
    files=args.files,
    allow_trailing_whitespace=args.allow_trailing_whitespace,
):
    tidy(files, allow_trailing_whitespace)
