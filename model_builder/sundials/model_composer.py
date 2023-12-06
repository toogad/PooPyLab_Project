#!/usr/bin/python3

def _create_var_defs(template_items={}):
    _vd = list(template_items.values())
    array_name = [s+'_' for s in _vd[:-1]]
    array_name.append('array['+template_items['NUM_MODEL_COMPONENTS']+']')
    return array_name

if __name__ == '__main__':
    lines = []
    items = {}
    with open('pipe.ppm', 'r') as def_file:
        lines = def_file.readlines()
        items = {it.split('=')[0]: it.split('=')[1][:-1] for it in lines}
    print(lines)
    print(items)
    print(_create_var_defs(items))
