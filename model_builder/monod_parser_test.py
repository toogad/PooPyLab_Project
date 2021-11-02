#!/usr/bin/python3

class expr_tree_node():
    def __init__(self, txt='', leftchild=None, rightchild=None):
        self.string = txt
        self.left = leftchild
        self.right = rightchild
        self.priority = (txt == '*' or txt == '/')  # 1 if * or /; 0 otherwise
        return None


def is_operator(char=''):
    """ check whether a character is '+', '-', '*', or '/' """

    return (char == '+' or char == '-' or char == '*' or char == '/')


def has_operator(term=[]):
    """ check whether a term contain '+', '-', '*', or '/' """

    return ('+' in term or '-' in term or '*' in term or '/' in term)


def create_var(expr='', start=0):
    var = ''
    operator = ''
    for ch in expr[start:]:
        if ch.isalpha() or ch.isnumeric() or ch == '_':
            var += ch
        elif is_operator(ch):
            operator = ch
            break
        elif ch != ' ':
            print("INVALID CHARACTER DETECTED. ABORTED PROCESS.")
            return '', 0, ''

    return var, len(var) + len(operator), operator


def build_tree(expr='A-B+K-C*D+E/F*G', start=0, unfinished=[], treetop=None):
    if start >= len(expr):
        return treetop

    var, offset, operator = create_var(expr, start)

    newchild = expr_tree_node(var, None, None)
    newparent = expr_tree_node(operator, newchild, build_tree(expr, start+offset, unfinished, treetop))

    if treetop is None:
        treetop = newparent
        unfinished.append(newparent)
        newparent.rt_child = build_tree(expr, start+offset, unfinished, treetop)
        return treetop

    if len(unfinished):
        if unfinished[-1].priority == newparent.priority:
            v = unfinished.pop()
            v.right = newchild
            treetop = newparent
            treetop.left = v
        else



    return

if __name__ == '__main__':

    from model_writer import parse_monod, find_num_denom

    #monod = '  ((  (((X_S)) /(X_BH+(   S_O   )))))  / (( K _  X  +(  (X_S ) /  X_BH))  ) '
    combo = ' ( S_O / ( K_OH + S_O ) + cf_h * K_OH / ( K_OH + S_O) * S_NO / (K_NO+S_NO))'
    print('Monod term before parsing:', combo)

    parsed = parse_monod(combo)
    print(parsed)

    numerator, denominator = find_num_denom(parsed)
    print('Numerator =', numerator, '; Denominator =', denominator)
    print('Numerator is a sub-term in Denominator:', numerator in denominator)

