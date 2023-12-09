#!/usr/bin/python3

def create_configs(filename='pipe.ppm'):
    lines, items = [], {}
    with open(filename, 'r') as def_file:
        lines = def_file.readlines()
        items = {it.split('=')[0]: it.split('=')[1][:-1] for it in lines}
    return items


def _create_array_name(template_items={}, branch='Inlet'):
    array_str = 'comp'
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

def define_branch_arrays(items={}):
    array_defs = []
    # A process unit may not have an inlet, e.g. an Influent
    # A process unit may not have a main outlet, e.g. an Effluent or a WAS
    # A process unit may not have a side outlet, e.g. a Pipe or a CSTR
    if items['INLET_NAME']:
        array_defs.append(_create_array_name(items, 'Inlet'))
    if items['MAIN_OUTLET_NAME']:
        array_defs.append(_create_array_name(items, 'Main'))
    if items['SIDE_OUTLET_NAME']:
        array_defs.append(_create_array_name(items, 'Side'))

    return ', '.join(array_defs)


def compose_eqns(model_files=[]):
    configs = [create_configs(f) for f in model_files]
    declars = ['realtype '+define_branch_arrays(items)+';' for items in configs]
    #all_eqs = []

    return declars


def write_to_file(filename='syseqs.c', lines=[], write_mode='w'):
    with open(filename, write_mode) as eqf:
        for declaration in lines:
            eqf.write(declaration)
            eqf.write('\n')
    return None


if __name__ == '__main__':
    p1_config = create_configs('pipe.ppm')
    p1_array_defs = define_branch_arrays(p1_config)
    print(p1_array_defs)
    inf1_config = create_configs('influent.ppm')
    inf1_array_defs = define_branch_arrays(inf1_config)
    print(inf1_array_defs)
    declars = compose_eqns(['pipe.ppm', 'influent.ppm'])
    write_to_file('syseqs.c', declars, 'w')
