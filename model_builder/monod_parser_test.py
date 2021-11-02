#!/usr/bin/python3

class expr_tree_node():
    def __init__(self, char=''):
        self.text = char
        self.lt_child = None
        self.rt_child = None
        return None


def _is_operator(char=''):
    """ check whether a character is '+', '-', '*', or '/' """

    return (char == '+' or char == '-' or char == '*' or char == '/')


def _has_operator(term=[]):
    """ check whether a term contain '+', '-', '*', or '/' """

    return ('+' in term or '-' in term or '*' in term or '/' in term)


def _is_parenthesis(char=''):
    if char == '(':
        return 1
    elif char == ')':
        return 2
    else:
        return 0


def create_node(text='', left_child=None, right_child=None):
    _newnode = expr_tree_node()
    _newnode.text = text
    _newnode.lt_child = left_child
    _newnode.rt_child = right_child
    return _newnode


def build_tree(expr='A-B+C*D+E/F*G', start=0, stack=[], treetop=None):
    _scan = ''
             

            
            
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

