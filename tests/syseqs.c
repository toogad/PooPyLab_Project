sunrealtype Influent_1_mo_comp[14];
sunrealtype Pipe_1_in_comp[14], Pipe_1_mo_comp[14];
// unit Pipe_2 with incomplete connection here;
sunrealtype ASMReactor_1_in_comp[14], ASMReactor_1_mo_comp[14];
sunrealtype FinalClarifier_1_in_comp[14], FinalClarifier_1_mo_comp[14], FinalClarifier_1_so_comp[14];
sunrealtype WAS_1_in_comp[14];
sunrealtype Splitter_1_in_comp[14], Splitter_1_mo_comp[14], Splitter_1_so_comp[14];
sunrealtype Effluent_1_in_comp[14];
int i;
for(i=0; i<14; i++)
  Influent_1_mo_comp[i] = Ith(y, 0+i+1);

for(i=0; i<14; i++)
  Pipe_1_in_comp[i] = Ith(y, 14+i+1);

for(i=0; i<14; i++)
   Pipe_1_mo_comp[i] = Ith(y, 28+i+1);

for(i=0; i<14; i++)
  ASMReactor_1_in_comp[i] = Ith(y, 42+i+1);

for(i=0; i<14; i++)
   ASMReactor_1_mo_comp[i] = Ith(y, 56+i+1);

for(i=0; i<14; i++)
  FinalClarifier_1_in_comp[i] = Ith(y, 70+i+1);

for(i=0; i<14; i++)
   FinalClarifier_1_mo_comp[i] = Ith(y, 84+i+1);

for(i=0; i<14; i++)
   FinalClarifier_1_so_comp[i] = Ith(y, 98+i+1);

for(i=0; i<14; i++)
  WAS_1_in_comp[i] = Ith(y, 112+i+1);

for(i=0; i<14; i++)
  Splitter_1_in_comp[i] = Ith(y, 126+i+1);

for(i=0; i<14; i++)
   Splitter_1_mo_comp[i] = Ith(y, 140+i+1);

for(i=0; i<14; i++)
   Splitter_1_so_comp[i] = Ith(y, 154+i+1);

for(i=0; i<14; i++)
  Effluent_1_in_comp[i] = Ith(y, 168+i+1);

LHS(0) = Influent_1_in_comp[0] - 

// ERROR in Influent_1's inlet connection.
for (i=1; i<14; i++){
  LHS[14+i] = Influent_1_in_comp[i] - INF1_Influent_2_mo_comp[i];
  LHS[28+i] = P1_Pipe_1_in_comp[i] - P1_Pipe_1_mo_comp[i];
}

LHS(42) = Pipe_1_in_comp[0] - Influent_1_mo_comp[0]

for(i=1; i<14; i++)
  LHS(43+i) = Pipe_1_in_comp[i] - Influent_1_mo_comp[i];

for (i=1; i<14; i++){
  LHS[56+i] = Pipe_1_in_comp[i] - INF1_Influent_2_mo_comp[i];
  LHS[70+i] = P1_Pipe_1_in_comp[i] - P1_Pipe_1_mo_comp[i];
}

LHS(84) = Pipe_2_in_comp[0] - 

// ERROR in Pipe_2's inlet connection.
for (i=1; i<14; i++){
  LHS[98+i] = Pipe_2_in_comp[i] - INF1_Influent_2_mo_comp[i];
  LHS[112+i] = P1_Pipe_1_in_comp[i] - P1_Pipe_1_mo_comp[i];
}

LHS(126) = ASMReactor_1_in_comp[0] - Splitter_1_mo_comp[0] - Pipe_1_mo_comp[0]

for(i=1; i<14; i++)
  LHS(127+i) = ASMReactor_1_in_comp[i] - (Splitter_1_mo_comp[i] * Splitter_1_mo_comp[0]Pipe_1_mo_comp[i] * Pipe_1_mo_comp[0]) / ASMReactor_1_in_comp[0];

for (i=1; i<14; i++){
  LHS[140+i] = ASMReactor_1_in_comp[i] - INF1_Influent_2_mo_comp[i];
  LHS[154+i] = P1_Pipe_1_in_comp[i] - P1_Pipe_1_mo_comp[i];
}

LHS(168) = FinalClarifier_1_in_comp[0] - ASMReactor_1_mo_comp[0]

for(i=1; i<14; i++)
  LHS(169+i) = FinalClarifier_1_in_comp[i] - ASMReactor_1_mo_comp[i];

for (i=1; i<14; i++){
  LHS[182+i] = FinalClarifier_1_in_comp[i] - INF1_Influent_2_mo_comp[i];
  LHS[196+i] = P1_Pipe_1_in_comp[i] - P1_Pipe_1_mo_comp[i];
}

LHS(210) = WAS_1_in_comp[0] - Splitter_1_so_comp[0]

for(i=1; i<14; i++)
  LHS(211+i) = WAS_1_in_comp[i] - Splitter_1_so_comp[i];

for (i=1; i<14; i++){
  LHS[224+i] = WAS_1_in_comp[i] - INF1_Influent_2_mo_comp[i];
  LHS[238+i] = P1_Pipe_1_in_comp[i] - P1_Pipe_1_mo_comp[i];
}

LHS(252) = Splitter_1_in_comp[0] - FinalClarifier_1_so_comp[0]

for(i=1; i<14; i++)
  LHS(253+i) = Splitter_1_in_comp[i] - FinalClarifier_1_so_comp[i];

for (i=1; i<14; i++){
  LHS[266+i] = Splitter_1_in_comp[i] - INF1_Influent_2_mo_comp[i];
  LHS[280+i] = P1_Pipe_1_in_comp[i] - P1_Pipe_1_mo_comp[i];
}

LHS(294) = Effluent_1_in_comp[0] - FinalClarifier_1_mo_comp[0]

for(i=1; i<14; i++)
  LHS(295+i) = Effluent_1_in_comp[i] - FinalClarifier_1_mo_comp[i];

for (i=1; i<14; i++){
  LHS[308+i] = Effluent_1_in_comp[i] - INF1_Influent_2_mo_comp[i];
  LHS[322+i] = P1_Pipe_1_in_comp[i] - P1_Pipe_1_mo_comp[i];
}

