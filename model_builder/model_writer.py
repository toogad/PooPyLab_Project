#!/usr/bin/python3

#   This file is part of PooPyLab.
#
#    PooPyLab is a simulation software for biological wastewater treatment processes using the International Water
#    Association Activated Sludge Models.
#
#    Copyright (C) Kai Zhang
#
#    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
#    License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any
#    later version.
#
#    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
#    warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
#    details.
#
#    You should have received a copy of the GNU General Public License along with this program. If not, see
#    <http://www.gnu.org/licenses/>.
#
#
#  Definition of the equation writing functions.
#

def set_model_components(all_rows):
    """ Initialize lists for model components and their names."""

    _num_comps = len([cell for cell in all_rows[0] if cell != ''])
    _comp_vals = [0.0] * _num_comps  # this may be unnecessary
    _comps = []

    for i in range(_num_comps):
        _comps.append([_comp_vals[i], all_rows[1][i], all_rows[2][i], all_rows[3][i]])

    return _comps


def set_model_params(all_rows=[]):
    """ Initialize the model parameters. """
    _params = {}

    # first row of actual parameter list
    _frap = all_rows.index([_row for _row in all_rows if _row[0] == 'PARAMETERS'][0]) + 1
    for row in all_rows[_frap:]:
        _params[row[0]] = row[1:5]

    return _params


if __name__ == '__main__':

    import csv

    csv_rows = []

    with open("template_asm1.csv", 'r') as csvf:
        r = csv.reader(csvf)
        for row in r:
            csv_rows.append(row)
            print(row)
    csvf.close()

    print()

    model_comps = set_model_components(csv_rows)

    print(model_comps)

    model_params = set_model_params(csv_rows)

    print(model_params)



#    with open("model.csv", 'r') as csvf:
#        dr = csv.DictReader(csvf)
#        for row in dr:
#            print(row)
#    csvf.close()
#
#    with open("model.csv", 'r') as csvf:
#        dr = csv.DictReader(csvf)
#        for row in dr:
#            print(row.keys())
#            print(row.values())
#    csvf.close()
#
