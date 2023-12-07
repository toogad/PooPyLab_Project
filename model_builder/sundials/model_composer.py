#!/usr/bin/python3

def _create_var_defs(template_items={}, array_str='comp', branch='inlet'):
    _vd = list(template_items.values())
    array_name = '_'.join(_vd[1:4])
    # template_items['NUM_MODEL_COMPONENTS'] excludes flow rate
    # adding 1 to the array length so that array[0] = flow rate
    # and the model components in the array jive with the human math
    array_len = int(template_items['NUM_MODEL_COMPONENTS']) + 1
    if branch == 'Inlet':
        prefix = '_in_'
    elif branch == 'Main':
        prefix = '_mo_'
    else:
        prefix = '_so_'
    array_name += prefix + array_str + '[' + str(array_len) + ']'
    # define the array as the SUNDIALS "realtype"
    return 'realtype ' + ''.join(array_name)


if __name__ == '__main__':
    lines, items = [], {}
    with open('pipe.ppm', 'r') as def_file:
        lines = def_file.readlines()
        items = {it.split('=')[0]: it.split('=')[1][:-1] for it in lines}
    in_comp_array_def = _create_var_defs(items, 'comp', 'Inlet')
    if items['MAIN_OUTLET_NAME']:
        mo_comp_array_def = _create_var_defs(items, 'comp', 'Main')
    if items['SIDE_OUTLET_NAME']:
        so_comp_array_def = _create_var_defs(items, 'comp', 'Side')
    else:
        so_comp_array_def = ''

    print(in_comp_array_def, mo_comp_array_def, so_comp_array_def)
    print(items)
