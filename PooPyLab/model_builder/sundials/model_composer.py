#!/usr/bin/python3

#def create_configs(filename='pipe.pmt'):
#    """
#    Read the lines in a .pmt file and convert the info into a dict
#
#    Args:
#        filename: the name for a .pmt file
#
#    Return:
#        {}
#    """
#    lines, items = [], {}
#    with open(filename, 'r') as def_file:
#        lines = def_file.readlines()
#        items = {it.split('=')[0]: it.split('=')[1][:-1] for it in lines}
#    return items


def _create_array_name(proc_unit={}, branch='Inlet'):
    """
    Create the array name for a particular branch of a process unit

    Args:
        proc_unit: a process unit's config {}
        branch: type of the branch whose array is to be created, 'Inlet'|'Main'|'Side'

    Return:
        str of the array name for the given branch
    """
    #
    # proc_unit['NUM_MODEL_COMPONENTS'] INCLUDES flow rate
    # array[0] = flow rate
    #
    array_name = [ proc_unit[branch + '_Arrayname'] + '[' + proc_unit['Num_Model_Components'] + ']' ]

    return ''.join(array_name)


def define_branch_arrays(unit={}):
    array_defs = []

    # A process unit may not have an inlet, e.g. an Influent
    if unit['Inlet_Codenames'] != 'None':
        array_defs.append(_create_array_name(unit, 'Inlet'))

    # A process unit may not have a main outlet, e.g. an Effluent or a WAS
    if unit['Main_Outlet_Codename'] != 'None':
        array_defs.append(_create_array_name(unit, 'Main_Outlet'))

    # A process unit may not have a side outlet, e.g. a Pipe or a CSTR
    if unit['Side_Outlet_Codename'] != 'None':
        array_defs.append(_create_array_name(unit, 'Side_Outlet'))

    if array_defs:
        return ', '.join(array_defs)

    return '// unit ' + unit['Codename'] + ' with incomplete connection here'


def assign_solver_array(arraynames=[], num_model_components=14):
    assignment = []
    counter = 0
    for group in arraynames:
        if group[:2] != '//':
            arrs = group.split(',')
            for branch_arr in arrs:
                assignment.append(
                    'for(i=0; i<' + str(num_model_components) + "; i++)\n"
                    + '  ' + branch_arr.split('[')[0] + '[i] = Ith(y, ' + str(counter) + "+i+1);\n")
                counter += num_model_components
    return assignment


def substitue_pipe_model(unit):
    selected_model = []
    accept = False
    with open(unit['Model_File_Path'], 'rt') as tf:
        for line in tf:
            if unit['MO_Flow_Data_Source'] in line or accept == True:
                accept = True
            if accept == True and line[0] != '#' and ('[' not in line) and (']' not in line):
                selected_model.append(line)
            elif selected_model and (unit['MO_Flow_Data_Source'] not in line) and ('[' in line and ']' in line):
                break
    return selected_model


def _get_flow_weighted_avg_inlet_concs(pfd, unit):
    inlet_streams = []
    myinlet = unit['Inlet_Codenames'].split()
    for codename in myinlet:
        discharger = pfd['Flowsheet'][codename]
        if discharger['Main_Outlet_Codename'] == unit['Codename']:
            inlet_streams.append() #TODO: continue here

    return


def compose_sys(pfd={}, tab=2):
    """
    Compose the units' variable/array declarations and mass balance equations

    Args:
        pfd: dict storing the process flowsheet

    Return:
        declaration of the arrays
        equations of all the units in pfd
    """
    # declare the arrays as SUNDIALS realtype
    array_names = ['//Error in ' + unit['Codename'] + ' configs...' if define_branch_arrays(unit) == ''
                   else define_branch_arrays(unit) + ';'
                   for unit in pfd["Flowsheet"].values()]
    declars = ['sunrealtype ' + aname if aname[:2] != '//'
               else aname
               for aname in array_names]
    declars.append('int i;')

    nc = int(list(pfd['Flowsheet'].values())[0]['Num_Model_Components'])  # No. of model Components
    array_assign = assign_solver_array(array_names, nc)

    all_eqs = []
    id_eq = 0
    for c in pfd['Flowsheet'].values():
        print(c['Codename'])
        if c['Type'] == 'Pipe':
            all_eqs.append('for (i=0; i<' + c['Num_Model_Components'] + '; i++){')
            all_eqs.append(' ' * tab
                           + 'LHS[' + str(id_eq) + '+i] = '
                           + c['Codename'] + '_in_comp[i]'
                           + '- INF1_Influent_2_mo_comp[i];')
            id_eq += int(c['Num_Model_Components'])
            all_eqs.append('  LHS[' + str(id_eq) + '+i] = P1_Pipe_1_in_comp[i] - P1_Pipe_1_mo_comp[i];')
            id_eq += int(c['Num_Model_Components'])
            all_eqs.append('}')

    return declars, array_assign, all_eqs


def write_to_file(filename='syseqs.c', lines=[], write_mode='w'):
    with open(filename, write_mode) as eqf:
        for item in lines:
            eqf.write(item)
            eqf.write('\n')
    return None
