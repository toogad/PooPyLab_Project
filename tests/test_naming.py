
from PooPyLab.unit_procs.streams import splitter, influent, effluent, WAS, pipe
from PooPyLab.unit_procs.physchem import final_clarifier
from PooPyLab.unit_procs.bio import asm_reactor


if __name__ == '__main__':
    a = splitter()
    print('a default name is', a.get_name())
    print('a default codename is', a.get_codename())
    a.set_name('goofy')
    print('a new name is', a.get_name())
    print('a new codename is', a.get_codename())

    c = pipe()
    print('c default names:', c.get_name(), c.get_codename())
    c.set_name('pluto')
    print('c new names:', c.get_name(), c.get_codename())

    d = influent()
    print('d default names:', d.get_name(), d.get_codename())
    d.set_name('pluto')  # purposefully
    print('d new names:', d.get_name(), d.get_codename())

    e = effluent()
    print('e default names:', e.get_name(), e.get_codename())
    e.set_name()  # purposefully
    print('e new names:', e.get_name(), e.get_codename())

    f = WAS()
    print('f default names:', f.get_name(), f.get_codename())
    f.set_name('blutbad')  # purposefully
    print('f new names:', f.get_name(), f.get_codename())

    h = final_clarifier()
    print('h default names:', h.get_name(), h.get_codename())
    h.set_name('blutbad')  # purposefully
    print('h new names:', h.get_name(), h.get_codename())

    i = asm_reactor()
    print('i default names:', i.get_name(), i.get_codename())
    i.set_name('grimm')  # purposefully
    print('i new names:', i.get_name(), i.get_codename())


    a.save('testsave.pfd',0)
    c.save('testsave.pfd',1)
