#include "utilities.h"

void PrintOutput(N_Vector y, int neq, realtype vol)
{
  int i;
  realtype SolidsInventory;

  printf("y =");
#if defined(SUNDIALS_EXTENDED_PRECISION)
  for (i = 1; i < neq+1; i++) printf(" %14.6Le", Ith(y,i));
#elif defined(SUNDIALS_DOUBLE_PRECISION)
  for (i = 1; i < neq+1; i++) printf(" %14.6e", Ith(y,i));
#else
  for (i = 1; i < neq+1; i++) printf(" %14.6e", Ith(y,i));
#endif
  printf("\n");

  SolidsInventory = (Ith(y,14) + Ith(y,16)) * vol * 1000; //mg as COD
  printf("SRT = %8f, HRT = %8f, Solids Inventory = %14.6f\n",
          SolidsInventory / (Ith(y,13) * 1000 * (Ith(y,14) + Ith(y,16))),
          vol / Ith(y,13),
          SolidsInventory);
  return;
}


int check_retval(void *retvalvalue, const char *funcname, int opt)
{
  int *errretval;

  /* Check if SUNDIALS function returned NULL pointer - no memory allocated */
  if (opt == 0 && retvalvalue == NULL) {
    fprintf(stderr,
            "\nSUNDIALS_ERROR: %s() failed - returned NULL pointer\n\n",
	    funcname);
    return(1);
  }

  /* Check if retval < 0 */
  else if (opt == 1) {
    errretval = (int *) retvalvalue;
    if (*errretval < 0) {
      fprintf(stderr,
              "\nSUNDIALS_ERROR: %s() failed with retval = %d\n\n",
	      funcname, *errretval);
      return(1);
    }
  }

  /* Check if function returned NULL pointer - no memory allocated */
  else if (opt == 2 && retvalvalue == NULL) {
    fprintf(stderr,
            "\nMEMORY_ERROR: %s() failed - returned NULL pointer\n\n",
	    funcname);
    return(1);
  }

  return(0);
}
