#!/usr/bin/python3

# This is to test the use of a py script to compile the SUNDIALS program.

import subprocess

if __name__ == '__main__':
    subprocess.run(["make", "clean"])
    subprocess.run(["make"])
    subprocess.run(["./sundials_ida_trial.out"])

