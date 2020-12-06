import setuptools

with open("README.md", "r") as fh:
    long_des = fh.read()

setuptools.setup(
    name='poopylab', 
    version='0.01.0.20201206', 
    author="Kai Zhang",
    author_email="poopylabproject@gmail.com",
    description="An open source simulation tool for biological wastewater treatment, by the poop nerds, for the the poop nerds.",
    long_description=long_des,
    long_description_content_type="text/markdown",
    keywords="Activated Sludge Model ASM Wastewater Simulation",
    url="https://github.com/toogad/PooPyLab_Project",
    project_urls={
        'Source': 'https://github.com/toogad/PooPyLab_Project',
        'Documentation': 'https://toogad.github.io/brownbook/index.html',
        'Tracker': 'https://github.com/toogad/PooPyLab_Project/issues', 
        'Funding': 'https://donate.pypi.org'
        },
    packages=setuptools.find_packages(include=['PooPyLab', 'PooPyLab.*']),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent"
        ],
    python_requires='>=3',
    install_requires=['scipy']
    )

