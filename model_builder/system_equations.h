
#ifndef SYSTEM__EQUATIONS
#define SYSTEM__EQUATIONS

#include <ida/ida.h>

// number of equations
#define NEQ 16

// system equations
int funcGrowth(realtype t, N_Vector y, N_Vector yp, N_Vector LHS, void *user_data);

#endif
