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


def _found_empty_operator(node_var, treetop, unfinished):
    u = unfinished.pop()
    u.right = node_var
    node_var.parent = u
    return treetop, unfinished


def _found_empty_treetop(node_var, node_ops, treetop, unfinished):
    treetop = [node_ops]
    node_ops.left = node_var
    node_var.parent = node_ops
    unfinished = [node_ops]
    return treetop, unfinished


def _connect_nodes(node_var, node_ops, treetop, unfinished):
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



def build_tree(expr=' B *  A / (Z*  ( D+ C* F )/ K - (G+H)*V )'):
    start = 0
    left_paren_count = 0
    queue = []
    print(expr)
    return create_nodes(expr, start, left_paren_count, queue)


def create_nodes(expr='B*A/(Z*(D+C*F)/K-(G+H)*V)', start=0, left_paren_count=0, queue=[]):
    temp = ''
    treetop = []
    unfinished = []
    while start < len(expr):
        ch = expr[start]
        start += 1
        if ch.isalpha() or ch.isnumeric() or ch == '_':
            temp += ch
        elif is_operator(ch):
            if temp != '':
                queue.append(expr_tree_node(temp))
            node_ops = expr_tree_node(ch)
            queue.append(node_ops)
            temp = ''
        elif ch == '(':
            next_left_paren_count = left_paren_count + 1
            next_level_queue = []
            node_var, start = create_nodes(expr, start, next_left_paren_count, next_level_queue)
            queue.append(node_var)
        elif ch == ')':
            if temp != '':
                queue.append(expr_tree_node(temp))
            temp = ''
            treetop = convert_queue_to_node(queue, [], [])
            queue.append(treetop[0])
            treetop[0].priority = -left_paren_count
            left_paren_count -= 1
            return treetop[0], start
        elif ch != ' ':
            print("INVALID CHARACTER DETECTED. ABORTED PROCESS.")

    if temp != '':
        queue.append(expr_tree_node(temp))

    treetop = convert_queue_to_node(queue, treetop, unfinished)
    return treetop[0], start


def convert_queue_to_node(queue=[], local_treetop=[], unfinished=[]):
    if len(queue) == 1 and len(unfinished) == 0:
        return queue[:]

    if len(queue):
        node_var = queue[0]
        queue.pop(0)
    else:
        return local_treetop

    # if the queue is not empty yet, get another node as "node_ops"
    if len(queue):
        node_ops = queue[0]
        queue.pop(0)
    else:  # reached the end of the queue
        local_treetop, unfinished = _found_empty_operator(node_var, local_treetop, unfinished)
        return local_treetop

    if len(local_treetop) == 0:
        local_treetop, unfinished = _found_empty_treetop(node_var, node_ops, local_treetop, unfinished)
        return convert_queue_to_node(queue, local_treetop, unfinished)

    local_treetop, unfinished = _connect_nodes(node_var, node_ops, local_treetop, unfinished)

    return convert_queue_to_node(queue, local_treetop, unfinished)



def print_tree(treetop):
    if treetop is None:
        return
    print(treetop.content)
    print_tree(treetop.left)
    print_tree(treetop.right)
    return



if __name__ == '__main__':

    monod = '  ((  (((X_S)) /(X_BH+(   S_O   )))))  / (( K _  X  +(  (X_S ) /  X_BH))  ) '
    #combo = ' ( S_O / ( K_OH + S_O ) + cf_h * K_OH / ( K_OH + S_O) * S_NO / (K_NO+S_NO))'

    #mytop = convert_expr_to_bin_subtree()
    #mytop, _ = build_tree('(D+C*F)/K')
    ##mytop, _ = build_tree()
    #mytop, _ = build_tree(combo)
    mytop, _ = build_tree(monod)
    print("regen:")
    print_tree(mytop)
