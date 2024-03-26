import context
from PooPyLab.unit_procs.streams import splitter, influent, effluent, WAS, pipe
from PooPyLab.unit_procs.physchem import final_clarifier
from PooPyLab.unit_procs.bio import asm_reactor

from PooPyLab.utils.pfd import show, check, save_wwtp, read_wwtp

if __name__ == '__main__':
    splt = splitter()
    print('splt id=', splt._id)
    inf = influent()
    print('inf id=', inf._id)
    p1 = pipe()
    print('p1 id=', p1._id)
    p2 = pipe()
    print('p2 id=', p2._id)
    eff = effluent()
    print('eff id=', eff._id)
    was = WAS()
    print('was id=', was._id)
    fc = final_clarifier()
    print('fc id=', fc._id)
    rxn = asm_reactor()
    print('rxn id=', rxn._id)

    print("INDIVIDUAL UNIT CONNECTION TESTING:")
    p1.add_upstream(inf, 'Main')
    print('p1 inlet:', [g.get_name() for g in p1.get_upstream()])
    print('inf main outlet:', inf.get_downstream_main().get_name())
    p1.remove_upstream(inf)
    print('after removal, p1 inlet:', [g.get_name() for g in p1.get_upstream()])
    print('inf main outlet:', inf.get_downstream_main())

    rxn.add_upstream(p1)
    print('rxn inlet:', [g.get_name() for g in rxn.get_upstream()])
    print('p1 main outlet:', p1.get_downstream_main().get_name())
    rxn.remove_upstream(p1)
    print('after removal, rxn inlet:', [g.get_name() for g in rxn.get_upstream()])
    print('p1 main outlet:', p1.get_downstream_main())

    fc.add_upstream(rxn, 'Main')
    print('fc inlet:', [g.get_name() for g in fc.get_upstream()])
    print('rxn main outlet:', rxn.get_downstream_main().get_name())
    fc.remove_upstream(rxn)
    print('after removal, fc inlet:', [g.get_name() for g in fc.get_upstream()])
    print('rxn main outlet:', rxn.get_downstream_main())

    print("\nWHOLE PLANT CONNECTION TEST:")
    splt.add_upstream(fc, 'Side')
    eff.add_upstream(fc, 'Main')
    rxn.add_upstream(splt, 'Main')
    was.add_upstream(splt, 'Side')
    was.remove_upstream(splt)

    splt.set_downstream_side(was)
    splt.set_as_SRT_controller()

    p1.add_upstream(inf, 'Main')
    rxn.add_upstream(p1, 'Main')

    fc.add_upstream(rxn, 'Main')

    print("FULL PLANT CONNECTION DISPLAY AND CHECK:")
    mywwtp = [inf, p1, p2, rxn, fc, was, splt, eff]
    show(mywwtp)
    check(mywwtp)

    global_params = {
        'Solids Retention Time': '10.0', #unit: day
        'Temperature': '15', #unit: degC
        'Site Elevation': '200' #unit: m above MSL
    }

    print("\nSAVING THE PLANT CONFIGURATION TO A JSON FILE:")
    save_wwtp(mywwtp, global_params, 'test_connect.json')

    # Corner cases: should show an error msg in each attempt
    print("\nCORNER CASES FOR CONNECTION:")
    inf.add_upstream(p1, 'Main')
    p2.add_upstream(was, 'Main')
    p2.add_upstream(p1, 'Side')
    eff.set_downstream_main(p2)

    print("READING PLANT CONFIGURATION FROM A JSON FILE:")
    mypfd = read_wwtp('test_connect.json')
    print(type(mypfd))
    print(mypfd["Flowsheet"]["Influent_1"])
