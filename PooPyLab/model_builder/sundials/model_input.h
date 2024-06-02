/* Influent Conditions - Steady State */

#ifndef MODEL__INPUT
#define MODEL__INPUT

#include <sundials/sundials_math.h>

#define X0    SUN_RCONST(2000.0)    /* initial y components */
#define S0    SUN_RCONST(1.0)
#define D0    SUN_RCONST(1.0e2)
#define VOL   SUN_RCONST(378000.0)
#define ONE   SUN_RCONST(1.0)
#define P1_IN_F SUN_RCONST(7800.0)
#define P1_IN_X SUN_RCONST(0.0)
#define P1_IN_S SUN_RCONST(395.0)
#define P1_IN_D SUN_RCONST(0.0)
#define P2_IN_F SUN_RCONST(30000.0)
#define P2_IN_X SUN_RCONST(0.0)
#define P2_IN_S SUN_RCONST(395.0)
#define P2_IN_D SUN_RCONST(0.0)

#endif
