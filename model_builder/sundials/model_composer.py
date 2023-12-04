#!/usr/bin/python3

if __name__ == '__main__':
    lines = []
    items = {}
    with open('pipe.ppm', 'r') as def_file:
        lines = def_file.readlines()
        items = {it.split('=')[0]: it.split('=')[1][:-1] for it in lines}
    print(lines)
    print(items)
