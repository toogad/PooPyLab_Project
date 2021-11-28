#!/usr/bin/python3

class expr_tree_node():
    def __init__(self, txt=''):
        self.content = txt
        self.parent = None
        self.left = None
        self.right = None
        if self.content == '+' or self.content == '-':
            self.priority = 3
        elif self.content == '*' or self.content == '/':
            self.priority = 2
        elif self.content == '(' or self.content == ')':
            self.priority = 1
        else:
            self.priority = 0
        return None


def is_operator(char=''):
    """ check whether a character is '+', '-', '*', or '/' """

    return (char == '+' or char == '-' or char == '*' or char == '/')


def has_operator(term=[]):
    """ check whether a term contain '+', '-', '*', or '/' """

    return ('+' in term or '-' in term or '*' in term or '/' in term)


""" BELOW HAS BEEN TESTED FOR EXPRESSIONS WITHOUT PARENTHESES

def get_var_ops(expr='', start=0):
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


def build_tree(expr='A-B+K-C*D+E/F*G', start=0, treetop=[], unfinished=[]):
    if start >= len(expr):
        return treetop[0]

    var, offset, operator = get_var_ops(expr, start)

    node_var = expr_tree_node(var, None, None, None)
    node_ops = expr_tree_node(operator, None, None, None)

    if node_ops.content == '':
        u = unfinished.pop()
        u.right = node_var
        node_var.parent = u
        return treetop[0]

    new_start = start + offset

    if len(treetop) == 0:
        treetop = [node_ops]
        node_ops.left = node_var
        node_var.parent = node_ops
        unfinished = [node_ops]
        return build_tree(expr, new_start, treetop, unfinished)

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

    return build_tree(expr, new_start, treetop, unfinished)


def convert_expr_to_bin_tree(expr=' A -B+K -  C  *D+E/F*G'):
    start = 0
    treetop = []
    unfinished = []
    print(expr)
    res = build_tree(expr, start, treetop, unfinished)
    return res


def convert_expr_to_bin_tree(expr=' A -B+K -  C  *D+E/F*G'):
    start = 0
    treetop = []
    unfinished = []
    print(expr)
    res = build_tree(expr, start, treetop, unfinished)
    return res

#ABOVE HAS BEEN TESTED FOR EXPRESSIONS WITHOUT PARENTHESES"""


def get_tree(expr=' A -B+K -  C  *D+E/F*G'):
    global_treetop = []
    global_unfinished = []
    parenth_index = []
    temp = ''

    index = 0

    while index < len(expr):
        ch = expr[index]

        if ch == '(':
            parenth_index.append(index)
        elif ch.isalpha() or ch.isnumeric() or ch == '_' or is_operator(ch):
            temp += ch
        elif ch == ')':  #TODO: continue from here
            node_var = convert_expr_to_bin_tree(temp)
            node_var.priority = -len(parenth_index)
            parenth_index.pop()
        elif ch != ' ':
            print("INVALID CHARACTER DETECTED. ABORTED PROCESS.")

        index += 1

        if index == len(expr):
            node_ops = expr_tree_node('')
            add_to_tree(node_var, node_ops, global_treetop, global_unfinished)

    return global_treetop[0]


def get_var_ops(expr='', start=0):
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


def build_tree(expr='A-B+K-C*D+E/F*G', start=0, treetop=[], unfinished=[]):
    if start >= len(expr):
        return treetop[0]

    var, offset, operator = get_var_ops(expr, start)

    node_var = expr_tree_node(var, None, None, None)
    node_ops = expr_tree_node(operator, None, None, None)

    if node_ops.content == '':
        u = unfinished.pop()
        u.right = node_var
        node_var.parent = u
        return treetop[0]

    new_start = start + offset

    if len(treetop) == 0:
        treetop = [node_ops]
        node_ops.left = node_var
        node_var.parent = node_ops
        unfinished = [node_ops]
        return build_tree(expr, new_start, treetop, unfinished)

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

    return build_tree(expr, new_start, treetop, unfinished)


def convert_expr_to_bin_tree(expr=' A -B+K -  C  *D+E/F*G'):
    start = 0
    treetop = []
    unfinished = []
    #pdb.set_trace()
    print(expr)
    res = build_tree(expr, start, treetop, unfinished)
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

    mytop = convert_expr_to_bin_tree()
    print("regen:")
    print_tree(mytop)
    
