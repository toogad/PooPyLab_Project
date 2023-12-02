/* -----------------------------------------------------------------
  Testing Sundials Nonlinear Solver with the following system:
    Pipe_1: Flow_1, X_1, S_1, D_1
    Pipe_2: Flow_1, X_1, S_1, D_1

    Pipe_1 & Pipe_2 Feed to Reactor R1 Inlet 
    
    Reactor R1:
    dX/dt = 0 = (Xi - X) / HRT + (  mu_max * (S/(Ks+S) - decay) * X
    dS/dt = 0 = (Si - S) / HRT + ( -mu_max * (S/(Ks+S) / Yh) + (1-kd) * decay) * X
    dD/dt = 0 = (Di - D) / HRT + kd * decay * X
 */

#include "utilities.h"
#include "model_constants.h"
#include "system_equations.h"
#include "model_input.h"


int funcGrowth(realtype t, N_Vector y, N_Vector yp, N_Vector LHS, void *user_data)
{
  realtype P1_mo_X, P1_mo_S, P1_mo_D, P1_mo_F;
  realtype P2_mo_X, P2_mo_S, P2_mo_D, P2_mo_F;
  realtype R1_in_X, R1_in_S, R1_in_D, R1_in_F;
  realtype R1_mo_X, R1_mo_S, R1_mo_D, R1_mo_F;


  P1_mo_F = Ith(y,1);  P1_mo_X = Ith(y,2);  P1_mo_S = Ith(y,3);  P1_mo_D = Ith(y,4);
  P2_mo_F = Ith(y,5);  P2_mo_X = Ith(y,6);  P2_mo_S = Ith(y,7);  P2_mo_D = Ith(y,8);
  R1_in_F = Ith(y,9);  R1_in_X = Ith(y,10); R1_in_S = Ith(y,11); R1_in_D = Ith(y,12);
  R1_mo_F = Ith(y,13); R1_mo_X = Ith(y,14); R1_mo_S = Ith(y,15); R1_mo_D = Ith(y,16);

  Ith(LHS,1) = P1_mo_F - P1_IN_F;
  Ith(LHS,2) = P1_mo_X - P1_IN_X;
  Ith(LHS,3) = P1_mo_S - P1_IN_S;
  Ith(LHS,4) = P1_mo_D - P1_IN_D;

  Ith(LHS,5) = P2_mo_F - P2_IN_F;
  Ith(LHS,6) = P2_mo_X - P2_IN_X;
  Ith(LHS,7) = P2_mo_S - P2_IN_S;
  Ith(LHS,8) = P2_mo_D - P2_IN_D;

  Ith(LHS,9) = R1_in_F - (P1_mo_F + P2_mo_F);
  Ith(LHS,10) = R1_in_X - ((P1_mo_F * P1_mo_X + P2_mo_F * P2_mo_X) / R1_in_F);
  Ith(LHS,11) = R1_in_S - ((P1_mo_F * P1_mo_S + P2_mo_F * P2_mo_S) / R1_in_F);
  Ith(LHS,12) = R1_in_D - ((P1_mo_F * P1_mo_D + P2_mo_F * P2_mo_D) / R1_in_F);

  Ith(LHS,13) = R1_mo_F - R1_in_F;

  Ith(LHS,14) = R1_mo_F / VOL * (R1_in_X - R1_mo_X)
                + (MU_MAX * R1_mo_S/(KS+R1_mo_S) - DECAY) * R1_mo_X
                - Ith(yp,14);

  Ith(LHS,15) = R1_mo_F / VOL * (R1_in_S - R1_mo_S)
                + (MU_MAX * R1_mo_S/(KS+R1_mo_S) / (-YH) + (ONE - KD) * DECAY) * R1_mo_X
                - Ith(yp,15);

  Ith(LHS,16) = R1_mo_F / VOL * (R1_in_D - R1_mo_D)
                + KD * DECAY * R1_mo_X
                - Ith(yp,16);

  return(0);
}

