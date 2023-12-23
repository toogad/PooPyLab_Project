
from PooPyLab.unit_procs.streams import splitter, influent, effluent, WAS, pipe
from PooPyLab.unit_procs.physchem import final_clarifier
from PooPyLab.unit_procs.bio import asm_reactor

from PooPyLab.utils.pfd import show

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

    rxn.add_upstream(p1)
    print('rxn inlet:', [g.get_name() for g in rxn.get_upstream()])
    print('p1 main outlet:', p1.get_downstream_main().get_name())
    rxn.remove_upstream(p1)
    print('rxn inlet:', [g.get_name() for g in rxn.get_upstream()])
    print('p1 main outlet:', p1.get_downstream_main())

    fc.add_upstream(rxn, 'Main')
    print('fc inlet:', [g.get_name() for g in fc.get_upstream()])
    print('rxn main outlet:', rxn.get_downstream_main().get_name())
    fc.remove_upstream(rxn)
    print('fc inlet:', [g.get_name() for g in fc.get_upstream()])
    print('rxn main outlet:', rxn.get_downstream_main())

    splt.add_upstream(fc, 'Side')
    eff.add_upstream(fc, 'Main')
    rxn.add_upstream(splt, 'Main')
    was.add_upstream(splt, 'Side')

    p1.add_upstream(inf, 'Main')
    rxn.add_upstream(p1, 'Main')

    fc.add_upstream(rxn, 'Main')

    pfd = [inf, p1, p2, rxn, fc, was, splt, eff]
    show(pfd)

    for i in range(len(pfd)):
        pfd[i].save('test_connect.pfd', i)
