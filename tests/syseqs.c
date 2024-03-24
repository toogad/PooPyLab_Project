sunrealtype Influent_1_mo_comp[14];
sunrealtype Pipe_1_in_comp[14], Pipe_1_mo_comp[14];
//Error in Pipe_2 configs...
sunrealtype ASMReactor_1_in_comp[14], ASMReactor_1_mo_comp[14];
sunrealtype FinalClarifier_1_in_comp[14], FinalClarifier_1_mo_comp[14], FinalClarifier_1_so_comp[14];
sunrealtype WAS_1_in_comp[14];
sunrealtype Splitter_1_in_comp[14], Splitter_1_mo_comp[14], Splitter_1_so_comp[14];
sunrealtype Effluent_1_in_comp[14];
int i;
for (i=0; i<14; i++){
  LHS[0+i] = Pipe_1_in_comp[i]- INF1_Influent_2_mo_comp[i];
  LHS[14+i] = P1_Pipe_1_in_comp[i] - P1_Pipe_1_mo_comp[i];
}
for (i=0; i<14; i++){
  LHS[28+i] = Pipe_2_in_comp[i]- INF1_Influent_2_mo_comp[i];
  LHS[42+i] = P1_Pipe_1_in_comp[i] - P1_Pipe_1_mo_comp[i];
}
