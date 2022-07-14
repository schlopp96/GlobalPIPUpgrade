import pathlib
from setuptools import setup, find_packages

readme = pathlib.Path("readme.md").read_text()
reqs = pathlib.Path("requirements.txt").read_text()
setup(
    name="UpgradePipPkgs",
    version="0.3.1",
    description=
    "Tool for upgrading all `pip` packages within a Python environment using just one command.",
    url='https://github.com/schlopp96/UpgradePipPkgs',
    author='schlopp96',
    author_email='schloppdaddy@gmail.com',
    long_description=readme,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[reqs],
    entry_points={
        'console_scripts': ['upgrade-pip-pkgs=UpgradePipPkgs.main:main']
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Archiving :: Packaging",
        "Environment :: Console ",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    keywords=[
        'upgrade', 'pip', 'pkgs', 'pkg', 'package', 'packages', 'update',
        'python', 'install', 'modules', 'module', 'installation', 'manager',
        'upgrades', 'updates'
    ])
