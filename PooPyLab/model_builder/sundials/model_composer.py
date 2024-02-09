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
    # proc_unit['NUM_MODEL_COMPONENTS'] INCLUDES flow rate
    # array[0] = flow rate
    array_len = int(proc_unit['Num_Model_Components'])
    if branch == 'Inlet':
        prefix = '_in_'
    elif branch == 'Main':
        prefix = '_mo_'
    else:
        prefix = '_so_'
    array_name = proc_unit['Codename'] + prefix + array_str + '[' + str(array_len) + ']'
    return ''.join(array_name)


def define_branch_arrays(unit={}):
    array_defs = []

    # A process unit may not have an inlet, e.g. an Influent
    if unit['Inlet_Codenames'] != 'None':
        array_defs.append(_create_array_name(unit, 'Inlet'))

    # A process unit may not have a main outlet, e.g. an Effluent or a WAS
    if unit['Main_Outlet_Codename'] != 'None':
        array_defs.append(_create_array_name(unit, 'Main'))

    # A process unit may not have a side outlet, e.g. a Pipe or a CSTR
    if unit['Side_Outlet_Codename'] != 'None':
        array_defs.append(_create_array_name(unit, 'Side'))

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
    declars = ['realtype '+define_branch_arrays(unit)+';' for unit in pfd["Flowsheet"].values()]
    declars.append('int i;')
    all_eqs = []
    num_eqs = 0
    for c in pfd['Flowsheet'].values():
        if c['Type'] == 'Pipe':
            all_eqs.append('for (i=0; i<' + c['Num_Model_Components'] + '; i++){')
            all_eqs.append('  LHS[i] = P1_Pipe_1_in_comp[i] - INF1_Influent_2_mo_comp[i];')
            num_eqs += int(c['Num_Model_Components']) + 1
            all_eqs.append('  LHS[' + str(num_eqs) + '+i] = P1_Pipe_1_in_comp[i] - P1_Pipe_1_mo_comp[i];')
            num_eqs += int(c['Num_Model_Components']) + 1
            all_eqs.append('}')
    return declars, all_eqs


def write_to_file(filename='syseqs.c', lines=[], write_mode='w'):
    with open(filename, write_mode) as eqf:
        for declaration in lines:
            eqf.write(declaration)
            eqf.write('\n')
    return None
