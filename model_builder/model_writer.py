#   This file is part of PooPyLab.
#
#    PooPyLab is a simulation software for biological wastewater treatment
#    processes using the International Water Association Activated Sludge
#    Models.
#   
#    Copyright (C) Kai Zhang
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
# --------------------------------------------------------------------
# Definition of the equation writing functions.
#

if __name__ == '__main__':

    import csv

    with open("template_asm1.csv", 'r') as csvf:
        r = csv.reader(csvf)
        for row in r:
            print(row)
    csvf.close()

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
