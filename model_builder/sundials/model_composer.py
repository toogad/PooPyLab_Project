#!/usr/bin/python3

def _create_array_name(template_items={}, array_str='comp', branch='Inlet'):
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
    return ''.join(array_name)

def define_branches(filename='pipe.ppm', array_str='comp'):
    lines, items, array_defs = [], {}, []
    with open(filename, 'r') as def_file:
        lines = def_file.readlines()
        items = {it.split('=')[0]: it.split('=')[1][:-1] for it in lines}
    #print(items)

    # A process unit may not have an inlet, e.g. an Influent
    # A process unit may not have a main outlet, e.g. an Effluent or a WAS
    # A process unit may not have a side outlet, e.g. a Pipe or a CSTR
    if items['INLET_NAME']:
        array_defs.append(_create_array_name(items, array_str, 'Inlet'))
    if items['MAIN_OUTLET_NAME']:
        array_defs.append(_create_array_name(items, array_str, 'Main'))
    if items['SIDE_OUTLET_NAME']:
        array_defs.append(_create_array_name(items, array_str, 'Side'))

    return 'realtype ' + ', '.join(array_defs)

if __name__ == '__main__':
    unit_arrays = define_branches('pipe.ppm', 'comp')
    print(unit_arrays)
