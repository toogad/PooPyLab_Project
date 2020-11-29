import setuptools

with open("README.md", "r") as fh:
    long_des = fh.read()

setuptools.setup(
    name='poopylab', 
    version='0.01.0.20201129', 
    author="Kai Zhang",
    author_email="poopylabproject@gmail.com",
    description="An open source simulation tool for biological wastewater treatment, by the poop nerds, for the the poop nerds.",
    long_description=long_des,
    long_description_content_type="text/markdown",
    keywords="ASM Wastewater Simulation",
    url="https://github.com/toogad/PooPyLabProject",
    packages=setuptools.find_packages(include=['PooPyLab', 'PooPyLab.*']),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent"
        ],
    python_requires='>=3',
    install_requires=['scipy']
    )

