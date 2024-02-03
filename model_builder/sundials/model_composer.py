#!/usr/bin/python3

def create_configs(filename='pipe.pmt'):
    """
    Read the lines in a .pmt file and convert the info into a dict

    Args:
        filename: the name for a .pmt file

    Return:
        {}
    """
    lines, items = [], {}
    with open(filename, 'r') as def_file:
        lines = def_file.readlines()
        items = {it.split('=')[0]: it.split('=')[1][:-1] for it in lines}
    return items


def _create_array_name(proc_unit={}, branch='Inlet'):
    """
    Create the array name for a particular branch of a process unit

    Args:
        proc_unit: a configs {}
        branch: type of the branch whose array is to be created, 'Inlet'|'Main'|'Side'

    Return:
        str of the array name for the given branch
    """
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


def compose_sys(pfd={}):
    """
    Compose the units' variable/array declarations and mass balance equations

    Args:
        pfd: dict storing the process flowsheet

    Return:
        declaration of the arrays
        equations of all the units in pfd
    """
    # declare the arrays as SUNDIALS realtype
    declars = ['realtype '+define_branch_arrays(items)+';' for items in configs]
    declars.append('int i;')
    all_eqs = []
    num_eqs = 0
    for c in configs:
        if c['SELF_TYPE'] == 'Pipe':
            all_eqs.append('for (i=0; i<' + c['NUM_MODEL_COMPONENTS'] + '; i++){')
            all_eqs.append('  LHS[i] = P1_Pipe_1_in_comp[i] - INF1_Influent_2_mo_comp[i];')
            num_eqs += int(configs[0]['NUM_MODEL_COMPONENTS']) + 1
            all_eqs.append('  LHS[' + str(num_eqs) + '+i] = P1_Pipe_1_in_comp[i] - P1_Pipe_1_mo_comp[i];')
            num_eqs += int(configs[0]['NUM_MODEL_COMPONENTS']) + 1
            all_eqs.append('}')
    return declars, all_eqs


def write_to_file(filename='syseqs.c', lines=[], write_mode='w'):
    with open(filename, write_mode) as eqf:
        for declaration in lines:
            eqf.write(declaration)
            eqf.write('\n')
    return None


if __name__ == '__main__':
    pfd = ['influent.pmt', 'pipe.pmt']
    declars, eqs = compose_sys(pfd)
    write_to_file('syseqs.c', declars, 'w')
    write_to_file('syseqs.c', eqs, 'a')
