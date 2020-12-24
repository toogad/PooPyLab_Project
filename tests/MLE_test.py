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
# 20201223 KZ: re-run after get_steady_state() interface update
# 20201129 KZ: re-run after package structure update
# 20201127 KZ: moved steps into utils.run.get_steady_state()
# 20200711 KZ: integrated the handling of a PFD w/o RAS/WAS
# 20200623 KZ: retested after updating steady state criteria
# 20191022 KZ: init and passed
#

from PooPyLab.utils import pfd, run

if __name__ == '__main__':

    import MLE

    wwtp = MLE.construct()

    pfd.check(wwtp)

    pfd.show(wwtp)

    run.get_steady_state(wwtp, target_SRT=MLE.SRT,
                            verbose=False,
                            diagnose=False,
                            mn='BDF',
                            fDO=True,
                            DOsat=10)

