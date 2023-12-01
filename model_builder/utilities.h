#ifndef UTILITIES__
#define UTILITIES__

#include <nvector/nvector_serial.h>

/* User-defined vector accessor macro: Ith */
/* This macro is defined in order to write code which exactly matches
   the mathematical problem description given above.

   Ith(v,i) references the ith component of the vector v, where i is in
   the range [1..NEQ] and NEQ is defined above. The Ith macro is defined
   using the N_VIth macro in nvector.h. N_VIth numbers the components of
   a vector starting from 0.
*/
#define Ith(v,i)    NV_Ith_S(v,i-1)       /* Ith numbers components 1..NEQ */

void PrintOutput(N_Vector u, int neq, realtype vol);
int check_retval(void *retvalvalue, const char *funcname, int opt);

#endif
