import context
from PooPyLab.utils.pfd import read_wwtp
from PooPyLab.model_builder.sundials.model_composer import compose_sys, write_to_file

mypfd = read_wwtp("test_connect.json")
declars, eqs = compose_sys(mypfd)
#print(declars)
#print(eqs)
write_to_file('syseqs.c', declars, 'w')
write_to_file('syseqs.c', eqs, 'a')
