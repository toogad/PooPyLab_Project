# This file is part of PooPyLab.
#
# PooPyLab is a simulation software for biological wastewater treatment processes using International Water Association
# Activated Sludge Models.
#
#    Copyright (C) Kai Zhang
#
#    PooPyLab is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
#    License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any
#    later version.
#
#    warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
#    details.
#
#    You should have received a copy of the GNU General Public License along with PooPyLab. If not, see
#    <http://www.gnu.org/licenses/>.
#
#
#    This is the definition of the ASM1 model to be imported as part of the Reactor object
#


def _create_array_name(proc_unit={}, branch='Inlet'):
    """ Create the array name for a particular branch of a process unit

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
    """ Define the array names for each available branch of a unit

    Args:
        unit: a PooPyLab process unit, {}

    Return:
        str of arraynames for the branches
    """

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
    """ Construct C code for assigning the variable array into the obj function

    Args:
        arraynames: list of array names
        num_model_components: number of model components, int.
    Return:
        assignment C code, str.
    """

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


def collect_inlet_arrays(pfd, unit):
    """ Generate the array names that are discharging to the current unit

    Args:
        pfd: dict storing the process flowsheet
        unit: the process unit whose inlet streams are to be identified

    Return:
        the identified inlet streams as an str
    """
    inlet_streams = []
    myinlet = unit['Inlet_Codenames'].split(' ')

    #TODO: add ERROR Handling here
    if myinlet == ['None']:
        return inlet_streams

    for codename in myinlet:
        discharger = pfd['Flowsheet'][codename]
        if discharger['Main_Outlet_Codename'] == unit['Codename']:
            inlet_streams.append(discharger['Main_Outlet_Arrayname'])
        else:
            inlet_streams.append(discharger['Side_Outlet_Arrayname'])

    return inlet_streams


def generate_inlet_flow(unit, inlet_streams, start_eq_id):
    """ Generate the totalizing ops in the equation system (.c file)

    Args:
        unit: the process unit whose inlet total flow is to be totalized
        inlet_streams: the identified inlet streams for "unit", []
        start_eq_id: starting equation id for the LHS, int

    Return:
        a str of the ops that sum up the total flow for the unit
        an updated start_eq_id
    """
    my_inlet_flow_str = unit['Inlet_Arrayname'] + '[0] - '
    totalizer_str = []

    for discharger in inlet_streams:
        totalizer_str.append(discharger + '[0]')
    return 'LHS[' + str(start_eq_id) + '] = ' + my_inlet_flow_str + ' - '.join(totalizer_str) + '\n', start_eq_id+1


def substr_for_flow(unit, flowstr, inlet_streams):
    """ Generate the substitution str for the flow in a model template

    Args:
        unit: the PooPyLab unit being worked on, {}
        flowstr: the flow term used in the model template, '':
        inlet_streams: the identified inlet streams for "unit", []

    Return:
        str of C array element to replace the flow term in the model template
    """
    branch = ''

    if flowstr == 'MY_IN_FLOW':
        branch = 'Inlet'
    elif flowstr == 'MY_MO_FLOW':
        branch = 'Main_Outlet'
    elif flowstr == 'MY_SO_FLOW':
        branch = 'Side_Outlet'

    if branch != '':
        return unit[branch + '_Arrayname'] + '[0]'

    totalizer_str = []
    if flowstr == 'DISCHARGERS_SUM':
        for discharger in inlet_streams:
            totalizer_str.append(discharger + '[0]')
        return '(' + ' + '.join(totalizer_str) + ')\n'

    if flowstr.isupper() or flowstr.islower() or flowstr.isnumeric():
        return 'ERROR'
    else:
        return ''



def generate_inlet_flow_weighted_avg(unit, inlet_streams, start_eq_id):
    """ Generate the flow weighted average inlet concentrations

    Args:
        unit: the process unit whose inlet concs are being determined
        inlet_streams: the inlet arrays for the 'unit'
        start_eq_id: starting equation id for the LHS, int

    Return:
        a str of C code to generate the flow weighted avg (model components),
        an updated eq_id

        Example:
        'for(j=1; j<14; j++)
           LHS[start_eq_id-1+j] = unit.in_comps[j]
                                  - (inlet_A[j]*inlet_A[0] + inlet_B[j]*inlet_B[0]) / unit.in_comps[0];'
    """
    n = len(inlet_streams)
    if n == 0:
        return '// ERROR in ' + unit['Codename'] + "'s inlet connection."

    fwavg = [ 'for(i=1; i<' + unit['Num_Model_Components'] + '; i++)\n' ]

    calcs = '  ' + 'LHS[' + str(start_eq_id - 1) + '+i] = ' + unit['Inlet_Arrayname'] + '[i] - '
    if n > 1:
        calcs += '(' + ''.join([dschg + '[i] * ' + dschg + '[0]' for dschg in inlet_streams]) + ')'
        calcs += ' / ' + unit['Inlet_Arrayname'] + '[0];\n'
    else: # n==1
        calcs += ''.join([dschg + '[i];\n' for dschg in inlet_streams])

    fwavg.append(calcs)

    return ''.join(fwavg), start_eq_id+int(unit['Num_Model_Components'])-1
