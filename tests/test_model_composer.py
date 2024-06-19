import context
from PooPyLab.utils.pfd import read_wwtp
from PooPyLab.model_builder.sundials.model_composer import compose_sys, write_to_file
#from PooPyLab.model_builder.sundials.model_composer import substitue_pipe_model

mypfd = read_wwtp("test_connect.json")
declars, assigns, eqs = compose_sys(mypfd)

write_to_file('syseqs.c', declars, 'w')
write_to_file('syseqs.c', assigns, 'a')
write_to_file('syseqs.c', eqs, 'a')

##for u in mypfd['Flowsheet'].values():
##    print(u['Codename'], ' ', u['Type'], ':')
##    if u['Type'] == 'Pipe':
##        pipe_model_template = substitue_pipe_model(u)
##        print(pipe_model_template)
