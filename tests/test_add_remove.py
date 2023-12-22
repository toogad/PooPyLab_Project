
from PooPyLab.unit_procs.streams import splitter, influent, effluent, WAS, pipe
from PooPyLab.unit_procs.physchem import final_clarifier
from PooPyLab.unit_procs.bio import asm_reactor


if __name__ == '__main__':
    splt = splitter()
    inf = influent()
    p1 = pipe()
    p2 = pipe()
    eff = effluent()
    was = WAS()
    fc = final_clarifier()
    rxn = asm_reactor()

    p1.add_upstream(inf, 'Main')
    print('p1 inlet:', [g.get_name() for g in p1.get_upstream()])
    print('inf main outlet:', inf.get_downstream_main().get_name())
    p1.remove_upstream(inf)
    print('p1 inlet:', [g.get_name() for g in p1.get_upstream()])
    print('inf main outlet:', inf.get_downstream_main())
    rxn.add_upstream(p1, 'Main')
    rxn.remove_upstream(p1)


    #a.save('testsave.pfd',0)
    #c.save('testsave.pfd',1)
