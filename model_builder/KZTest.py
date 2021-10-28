#  This file defines the model named KZTest
#
#  Created Using:            PooPyLab Model Builder
#  User Specified Model in:  template_asm1.csv
#  Created at:               21:19:12 2021-October-27
#


from .asmbase import asm_model


class KZTest(asm_model):
    def __init__(self, ww_temp=20, DO=2):
        """
        Args:
            ww_temp:    wastewater temperature, degC;
            DO:         dissoved oxygen, mg/L

        Return:
            None
        See:
            _set_ideal_kinetics_20C();
            _set_params();
            _set_stoichs().
        """

        asm_model.__init__(self)
        self.__class__.__id += 1

        self._set_ideal_kinetics_20C_to_defaults()

        # wastewater temperature used in the model, degC
        self._temperature = ww_temp

        # mixed liquor bulk dissolved oxygen, mg/L
        self._bulk_DO = DO

        # temperature difference b/t what's used and baseline (20C), degC
        self._delta_t = self._temperature - 20

        self.update(ww_temp, DO)

        # KZTest model components
        self._comps = [0.0] * 13

        # Intermediate results of rate expressions, M/L^3/T
        # The list is to help speed up the calculation by reducing redundant
        # calls of individual rate expressions in multiple mass balance equations
        # for the model components.
        # KZTest has 8 bio processes.
        self._rate_res = [0.0] * 8

        return None
