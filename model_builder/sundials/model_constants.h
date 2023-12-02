/* Model Constants */
/* TODO: Can be split into 2 files:
 *       one for stoichiometrics, and the other for kinetics
 */

#ifndef MODEL__CONSTANTS
#define MODEL__CONSTANTS

#include <sundials/sundials_types.h>

#define ZERO  RCONST(0.0)
#define MU_MAX RCONST(6.0)
#define DECAY RCONST(0.62)
#define KD    RCONST(0.08)
#define YH    RCONST(0.67)
#define KS    RCONST(10.0)

#endif
