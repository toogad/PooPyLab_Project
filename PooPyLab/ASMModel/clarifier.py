# This file is part of PooPyLab.
#
# PooPyLab is a simulation software for biological wastewater treatment
# processes using International Water Association Activated Sludge Models.
#    
#    Copyright (C) 2014  Kai Zhang
#
#    PooPyLab is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    PooPyLab is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with PooPyLab.  If not, see <http://www.gnu.org/licenses/>.
#
#
#    Definition of Primary and Final Clarifier units.
#    It is assumed that clarifiers are circular.
#    Author: Kai Zhang
#
#    Change Log: 
#        May 26, 2014 KZ: Changed base class from Base to Splitter
#        July 11, 2013 KZ: Initial commit
#

import splitter

class Final_Clarifier(splitter.Splitter):
    __id = 0
    def __init__(self, ActiveVol=380.0, SWD=3.5, Temperature=20.0, DO=2.0):
        splitter.Splitter.__init__(self)
        self.__class__.__id += 1
        self.__name__ = "FinalClarifier_" + str(self.__id)
        # SWD = side water depth in meters, default = ~12 ft
        # ActiveVol in m^3, default value equals to 100,000 gallons
        # Temperature = 20 C by default
        # DO = dissolved oxygen, default = 2.0 mg/L

        self._ActiveVol = ActiveVol
        self._SWD = SWD
        self._Area = self._ActiveVol / self._SWD
