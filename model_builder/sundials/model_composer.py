#!/usr/bin/python3

def _create_var_defs(template_items={}, array_str='comp'):
    _vd = list(template_items.values())
    array_name = '_'.join(_vd[:-1])
    #template_items['NUM_MODEL_COMPONENTS'] excludes flow rate
    #adding 1 to the array length so that array[0] = flow rate
    #and the model components in the array jive with the human math
    array_len = int(template_items['NUM_MODEL_COMPONENTS']) + 1
    array_name += '_' + array_str + '[' + str(array_len) + ']'
    return ''.join(array_name)


if __name__ == '__main__':
    lines = []
    items = {}
    with open('pipe.ppm', 'r') as def_file:
        lines = def_file.readlines()
        items = {it.split('=')[0]: it.split('=')[1][:-1] for it in lines}
    comp_array_def = "realtype " + _create_var_defs(items)
    print(comp_array_def)
