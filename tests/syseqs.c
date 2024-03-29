sunrealtype Influent_1_mo_comp[14];
sunrealtype Pipe_1_in_comp[14], Pipe_1_mo_comp[14];
//Error in Pipe_2 configs...
sunrealtype ASMReactor_1_in_comp[14], ASMReactor_1_mo_comp[14];
sunrealtype FinalClarifier_1_in_comp[14], FinalClarifier_1_mo_comp[14], FinalClarifier_1_so_comp[14];
sunrealtype WAS_1_in_comp[14];
sunrealtype Splitter_1_in_comp[14], Splitter_1_mo_comp[14], Splitter_1_so_comp[14];
sunrealtype Effluent_1_in_comp[14];
int i;
for(i=0; i<14; i++)
  Influent_1_mo_comp[i] = Ith(y, i+1);

for(i=14; i<28; i++)
  Pipe_1_in_comp[i] = Ith(y, i+1);

for(i=28; i<42; i++)
   Pipe_1_mo_comp[i] = Ith(y, i+1);

for(i=42; i<56; i++)
  ASMReactor_1_in_comp[i] = Ith(y, i+1);

for(i=56; i<70; i++)
   ASMReactor_1_mo_comp[i] = Ith(y, i+1);

for(i=70; i<84; i++)
  FinalClarifier_1_in_comp[i] = Ith(y, i+1);

for(i=84; i<98; i++)
   FinalClarifier_1_mo_comp[i] = Ith(y, i+1);

for(i=98; i<112; i++)
   FinalClarifier_1_so_comp[i] = Ith(y, i+1);

for(i=112; i<126; i++)
  WAS_1_in_comp[i] = Ith(y, i+1);

for(i=126; i<140; i++)
  Splitter_1_in_comp[i] = Ith(y, i+1);

for(i=140; i<154; i++)
   Splitter_1_mo_comp[i] = Ith(y, i+1);

for(i=154; i<168; i++)
   Splitter_1_so_comp[i] = Ith(y, i+1);

for(i=168; i<182; i++)
  Effluent_1_in_comp[i] = Ith(y, i+1);

for (i=0; i<14; i++){
  LHS[0+i] = Pipe_1_in_comp[i]- INF1_Influent_2_mo_comp[i];
  LHS[14+i] = P1_Pipe_1_in_comp[i] - P1_Pipe_1_mo_comp[i];
}
for (i=0; i<14; i++){
  LHS[28+i] = Pipe_2_in_comp[i]- INF1_Influent_2_mo_comp[i];
  LHS[42+i] = P1_Pipe_1_in_comp[i] - P1_Pipe_1_mo_comp[i];
}
