from setuptools import setup
from setuptools import find_packages
setup(name='gitignore-tidy',
      version='0.1',
      description='Tidy up your .gitignore file',
      author='Lorenz Walthert',
      author_email='lorenz.walthert@icloud.com',
      license='MIT',
      packages=find_packages(),
      entry_points = {
        'console_scripts': ['gitignore-tidy=gitignore_tidy.cli:main'],
    },
      zip_safe=False)