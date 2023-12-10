realtype INF1_Influent_2_mo_comp[4];
realtype P1_Pipe_1_in_comp[4], P1_Pipe_1_mo_comp[4];
int i;
for (i=0; i<3; i++){
  LHS[i] = P1_Pipe_1_in_comp[i] - INF1_Influent_2_mo_comp[i];
  LHS[i] = P1_Pipe_1_in_comp[i] - P1_Pipe_1_mo_comp[i];
}
