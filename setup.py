from setuptools import setup, find_packages
import re


def parse_requirements(file_name):
    requirements_ = []
    for line in open(file_name, 'r').read().split('\n'):
        if re.match(r'(\s*#)|(\s*$)', line):
            continue
        if re.match(r'\s*-e\s+', line):
            requirements_.append(re.sub(r'\s*-e\s+.*#egg=(.*)$', r'\1', line))
        elif re.match(r'\s*-f\s+', line):
            pass
        else:
            requirements_.append(line)
    return requirements_

requirements = parse_requirements('requirements.txt')

setup(
    name="Aryas",
    version="0.1",
    packages=find_packages(exclude="tests"),
    long_description=open('README.md').read(),
    install_requires=requirements,
    setup_requires=requirements,
    entry_points={'console_scripts': ['aryas=aryas.__main__:main']},
    scripts=['bin/aryas'],
)
