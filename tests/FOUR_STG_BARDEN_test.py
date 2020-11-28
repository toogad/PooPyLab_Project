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
#    Testing the influent/effluent/pipe/reactor classes.
#
#
# Change Log:
# 20200711 KZ: integrated the handling of a PFD w/o RAS/WAS
# 20191029 KZ: init and passed
#

import utils.pfd
import utils.run

if __name__ == '__main__':

    import FOUR_STG_BARDEN 

    wwtp = FOUR_STG_BARDEN.construct()

    utils.pfd.check(wwtp)

    utils.pfd.show(wwtp)

    utils.run.get_steady_state(wwtp, FOUR_STG_BARDEN.SRT)

