#!/usr/bin/python3

# =========Common Definitions Begin=========================
class expr_tree_node():
    def __init__(self, txt=''):
        self.content = txt
        self.parent = None
        self.left = None
        self.right = None
        if self.content == '+' or self.content == '-':
            self.priority = 2
        elif self.content == '*' or self.content == '/':
            self.priority = 1
        #elif self.content == '(' or self.content == ')':
        #    self.priority = 1
        else:
            self.priority = 0
        return None


def is_operator(char=''):
    """ check whether a character is '+', '-', '*', or '/' """

    return (char == '+' or char == '-' or char == '*' or char == '/')


def has_operator(term=[]):
    """ check whether a term contain '+', '-', '*', or '/' """

    return ('+' in term or '-' in term or '*' in term or '/' in term)


def found_empty_operator(node_var, treetop, unfinished):
    u = unfinished.pop()
    u.right = node_var
    node_var.parent = u
    return treetop, unfinished


def found_empty_treetop(node_var, node_ops, treetop, unfinished):
    treetop = [node_ops]
    node_ops.left = node_var
    node_var.parent = node_ops
    unfinished = [node_ops]
    return treetop, unfinished


def connect_nodes(node_var, node_ops, treetop, unfinished):
    if treetop[0].priority > node_ops.priority:
        u = unfinished.pop()
        if u.priority <= node_ops.priority:
            u.right = node_var
            node_var.parent = u
            node_ops.parent = u.parent
            node_ops.parent.right = node_ops
            node_ops.left = u
            unfinished = [node_ops]
        else:
            u.right = node_ops
            node_ops.parent = u
            node_ops.left = node_var
            node_var.parent = node_ops
            unfinished = [node_ops]
    else:
        node_ops.left = treetop[0]
        treetop[0].parent = node_ops
        u = unfinished.pop()
        u.right = node_var
        node_var.parent = u
        treetop = [node_ops]
        unfinished = [treetop[0]]
    return treetop, unfinished

# ===========Common Definitions End=========================



def subtree_get_var_ops(expr='', start=0):
    variable = ''
    operator = ''
    counter = 0
    for ch in expr[start:]:
        counter += 1
        if ch.isalpha() or ch.isnumeric() or ch == '_':
            variable += ch
        elif is_operator(ch):
            operator = ch
            break
        elif ch != ' ':
            print("INVALID CHARACTER DETECTED. ABORTED PROCESS.")
            return '', 0, ''

    return variable, counter, operator


def build_subtree(expr='A-B+K-C*D+E/F*G', start=0, treetop=[], unfinished=[]):
    if start >= len(expr):
        return treetop[0]

    var, offset, operator = subtree_get_var_ops(expr, start)

    node_var = expr_tree_node(var)
    node_ops = expr_tree_node(operator)

    if node_ops.content == '':
        treetop, unfinished = found_empty_operator(node_var, treetop, unfinished)
        return treetop[0]

    new_start = start + offset

    if len(treetop) == 0:
        treetop, unfinished = found_empty_treetop(node_var, node_ops, treetop, unfinished)
        return build_subtree(expr, new_start, treetop, unfinished)

    treetop, unfinished = connect_nodes(node_var, node_ops, treetop, unfinished)

    return build_subtree(expr, new_start, treetop, unfinished)


def convert_expr_to_bin_subtree(expr=' A -B+K -  C  *D+E/F*G'):
    start = 0
    treetop = []
    unfinished = []
    print(expr)
    #pdb.set_trace()
    res = build_subtree(expr, start, treetop, unfinished)
    return res


def print_tree(treetop):
    if treetop is None:
        return
    print(treetop.content)
    print_tree(treetop.left)
    print_tree(treetop.right)
    return



if __name__ == '__main__':

    #from model_writer import parse_monod, find_num_denom

    #monod = '  ((  (((X_S)) /(X_BH+(   S_O   )))))  / (( K _  X  +(  (X_S ) /  X_BH))  ) '
    #combo = ' ( S_O / ( K_OH + S_O ) + cf_h * K_OH / ( K_OH + S_O) * S_NO / (K_NO+S_NO))'
    #print('Monod term before parsing:', combo)

    #parsed = parse_monod(combo)
    #print(parsed)

    #numerator, denominator = find_num_denom(parsed)
    #print('Numerator =', numerator, '; Denominator =', denominator)
    #print('Numerator is a sub-term in Denominator:', numerator in denominator)

    import pdb
    mytop = convert_expr_to_bin_subtree()
    print("regen:")
    print_tree(mytop)

 
