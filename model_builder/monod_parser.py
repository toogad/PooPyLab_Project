#!/usr/bin/python3

if __name__ == '__main__':

    from model_writer import parse_monod, find_num_denom

    monod = '  ((  (((X_S)) /(X_BH+(   S_O   )))))  / (( K _  X  +(  (X_S ) /  X_BH))  ) '
    print('Monod term before parsing:', monod)

    parsed = parse_monod(monod)
    print(parsed)

    numerator, denominator = find_num_denom(parsed)
    print('Numerator =', numerator, '; Denominator =', denominator)
    print('Numerator is a sub-term in Denominator:', numerator in denominator)

