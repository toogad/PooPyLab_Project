/* Influent Conditions - Steady State */

#ifndef MODEL__INPUT
#define MODEL__INPUT

#include <sundials/sundials_math.h>

//TODO: all the model inputs will have to be in array form, read from a definition/data file

#define X0    RCONST(2000.0)    /* initial y components */
#define S0    RCONST(1.0)
#define D0    RCONST(1.0e2)
#define VOL   RCONST(378000.0)
#define ONE   RCONST(1.0)
#define P1_IN_F RCONST(7800.0)
#define P1_IN_X RCONST(0.0)
#define P1_IN_S RCONST(395.0)
#define P1_IN_D RCONST(0.0)
#define P2_IN_F RCONST(30000.0)
#define P2_IN_X RCONST(0.0)
#define P2_IN_S RCONST(395.0)
#define P2_IN_D RCONST(0.0)

#endif
