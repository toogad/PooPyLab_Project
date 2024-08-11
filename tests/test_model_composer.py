import context
from PooPyLab.utils.pfd import read_wwtp
from PooPyLab.model_builder.sundials.model_composer import compose_sys, write_to_file
#import pdb

mypfd = read_wwtp("test_connect.json")
#pdb.set_trace()
declars, assigns, eqs = compose_sys(mypfd)

write_to_file('syseqs.c', declars, 'w')
write_to_file('syseqs.c', assigns, 'a')
write_to_file('syseqs.c', eqs, 'a')
