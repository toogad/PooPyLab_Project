realtype Influent_1_mo_comp[14];
realtype Pipe_1_in_comp[14], Pipe_1_mo_comp[14];
realtype ;
realtype ASMReactor_1_in_comp[14], ASMReactor_1_mo_comp[14];
realtype FinalClarifier_1_in_comp[14], FinalClarifier_1_mo_comp[14], FinalClarifier_1_so_comp[14];
realtype WAS_1_in_comp[14];
realtype Splitter_1_in_comp[14], Splitter_1_mo_comp[14], Splitter_1_so_comp[14];
realtype Effluent_1_in_comp[14];
int i;
for (i=0; i<14; i++){
  LHS[i] = P1_Pipe_1_in_comp[i] - INF1_Influent_2_mo_comp[i];
  LHS[15+i] = P1_Pipe_1_in_comp[i] - P1_Pipe_1_mo_comp[i];
}
for (i=0; i<14; i++){
  LHS[i] = P1_Pipe_1_in_comp[i] - INF1_Influent_2_mo_comp[i];
  LHS[45+i] = P1_Pipe_1_in_comp[i] - P1_Pipe_1_mo_comp[i];
}
