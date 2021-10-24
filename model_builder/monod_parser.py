#!usr/bin/python3

#  This is a parser for the Monod terms in the PooPyLab model matrix.
#
#  The goals are:
#    1) Strip the potential Monod (or inhibition) terms;
#    2) Confirm the Monod/inhibition terms by checking their nominators and denominators;
#    3) Create a function call to calculate each Monod/inhibition term, store each result into a list
#    4) Create a dictionary to store the Monod/inhibition term and their "index" in the list in 3)
#
#

def find_num_denom(term='A/(K+A)'):
    if '/' not in term:
        print('Please present the Monod term in the format of "A/(K+A)" and retry.')
        return None

    _tsplt = term.split('/')

    _n = len(_tsplt)
    _main_divider_loc = _n // 2

    _numerator = ''
    _denominator = ''

    for _t in _tsplt[:_main_divider_loc]:
        _numerator += _t.strip() + '/'

    _numerator = _numerator.rstrip('/').strip()

    for _t in _tsplt[_main_divider_loc:]:
        _denominator += _t.strip() + '/'

    _denominator = _denominator.rstrip('/').strip()

    return _numerator, _denominator


def pop_to_left_parenth(stack=[]):
    """ pop the stack until the first '(' from the back """

    _res = []

    while len(stack) and '(' not in _res:
        _res.insert(0, stack.pop())

    return _res


def is_operan(char=''):
    return (char == '+' or char == '-' or char == '*' or char == '/')


def has_operan(term=[]):
    return ('+' in term or '-' in term or '*' in term or '/' in term)


def _reorg(expr='(K+A)', start=0, stack=[], found=[]):
    if start == len(expr):
        return

    _char = expr[start]

    if _char == ' ':
        # skip the blank (i.e. ' '):
        pass
    elif _char == '(':
        stack.append(_char)
    elif _char == ')':
        found += pop_to_left_parenth(stack)
        if has_operan(found):
            found += [')']
        else:
            found.pop(0)
        stack += found
        if start < len(expr) - 1:
            found.clear()
    elif _char.isalpha() or _char.isnumeric() or _char == '_' or is_operan(_char):
        stack.append(_char)
    else:
        print('Found invalid a character in the expression. Parsing aborted.')
        return

    _reorg(expr, start+1, stack, found)

    return


def term_scanner(expr=''):

    _chars = []
    return


if __name__ == '__main__':

    import pdb

    monod = '  (  (X_S) /X_BH)  / ( K_X  +X_S  /  X_BH)   '

    numerator, denominator = find_num_denom(monod)

    print('Numerator =', numerator, '; Denominator =', denominator)

    f = []
    _reorg(numerator, 0, [], f)
    print(''.join(f))

