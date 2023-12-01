#include <stdio.h>

#include <sundials/sundials_context.h>
#include <ida/ida.h>
#include <nvector/nvector_serial.h>
#include <sundials/sundials_nvector.h>
#include <sunnonlinsol/sunnonlinsol_newton.h>
#include <sunlinsol/sunlinsol_dense.h>
#include <sunmatrix/sunmatrix_dense.h>
#include <sundials/sundials_math.h>

#include "utilities.h"
#include "system_equations.h"
#include "model_input.h"



int main()
{
 
  SUNContext ctx;
  void *ida_mem;
  realtype t, t0, tf, tout, dt, tret;
  N_Vector yy, yp, yid, yy0_mod, yp0_mod;
  realtype rtol, atol;
  SUNMatrix A;
  SUNLinearSolver LS;
  SUNNonlinearSolver NLS;
  int retval, i;

  ida_mem = NULL;
  yy = NULL;
  A = NULL;
  LS = NULL;
  NLS = NULL;

  t0 = 0.0;        //move to macro
  tf = 100.0;      //move to macro
  tout = 1.0;      //move to macro
  dt = 1.0;        //move to macro

  rtol = 1.0e-14;  //move to macro
  atol = 1.0e-5;   //move to macro

  retval = SUNContext_Create(NULL, &ctx);

  yy = N_VNew_Serial(NEQ, ctx);
  /* Initial guess */
  Ith(yy,1) = 2000.0; Ith(yy,2) = X0; Ith(yy,3) = S0; Ith(yy,4) = D0;
  Ith(yy,5) = 2000.0; Ith(yy,6) = X0; Ith(yy,7) = S0; Ith(yy,8) = D0;
  Ith(yy,9) = 2000.0; Ith(yy,10) = X0; Ith(yy,11) = S0; Ith(yy,12) = D0;
  Ith(yy,13) = 2000.0; Ith(yy,14) = X0; Ith(yy,15) = S0; Ith(yy,16) = D0;

  yp = N_VNew_Serial(NEQ, ctx);
  for(i=1; i<NEQ+1; i++) Ith(yp,i) = 0.0;
  //Ith(yp,14) = 0.0; Ith(yp,15) = 0.0; Ith(yp,16) = 0.0;

  yid = N_VNew_Serial(NEQ, ctx);
  for(i=1; i<14; i++) Ith(yid,i) = 0.0;
  Ith(yid,14) = 1.0; Ith(yid,15) = 1.0; Ith(yid,16) = 1.0;
  printf("Y_id:"); PrintOutput(yid, NEQ, 0);


  A = SUNDenseMatrix(NEQ, NEQ, ctx);

  LS = SUNLinSol_Dense(yy, A, ctx);

  NLS = SUNNonlinSol_Newton(yy, ctx);

  ida_mem = IDACreate(ctx);
  retval = IDAInit(ida_mem, funcGrowth, t0, yy, yp);

  retval = IDASStolerances(ida_mem, rtol, atol);
  retval = IDASetLinearSolver(ida_mem, LS, A);
  retval = IDASetNonlinearSolver(ida_mem, NLS);

  yy0_mod = N_VNew_Serial(NEQ, ctx);
  yp0_mod = N_VNew_Serial(NEQ, ctx);
  retval = IDASetId(ida_mem, yid);
  retval = IDACalcIC(ida_mem, IDA_Y_INIT, tout); // use this to get the initial steady state before dynamic simulation
  retval = IDAGetConsistentIC(ida_mem, yy0_mod, yp0_mod);
  printf("Corrected Init Condition:\n");
  PrintOutput(yy0_mod, NEQ, 0); PrintOutput(yp0_mod, NEQ, 0);
//
  for (t=t0; t<tf; t++){
    retval = IDASolve(ida_mem, tout, &tret, yy, yp, IDA_NORMAL);
    printf("t=%f: ", tret);
    PrintOutput(yy, NEQ, VOL);
    if (check_retval(&retval, "IDASolve", 1)) break;
    if (retval == IDA_SUCCESS)
      tout += dt;
  }

  /* Print final statistics to the screen */
  printf("\nFinal Statistics:\n");
  retval = IDAPrintAllStats(ida_mem, stdout, SUN_OUTPUTFORMAT_TABLE);


  N_VDestroy(yy);
  N_VDestroy(yp);
  N_VDestroy(yid);
  N_VDestroy(yy0_mod);
  N_VDestroy(yp0_mod);
  IDAFree(&ida_mem);
  SUNLinSolFree_Dense(LS);
  SUNMatDestroy_Dense(A);
  SUNContext_Free(&ctx);

  return(retval);

}

