#!/usr/bin/python3

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

