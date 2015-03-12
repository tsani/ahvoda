import sys

if __name__ == '__main__':
    print('digraph Schema {')
    current_node = None
    for line in sys.stdin:
        line = line.strip()

        if not line:
            continue # skip empty lines

        if line.startswith('CREATE TABLE'):
            current_node = line.split(' ')[2]
        elif line.startswith('REFERENCES'):
            print(current_node, '->', line.split(' ')[1].strip(','), ';')
        else:
            print('skipping unrecognized line', file=sys.stderr)
    print('}')
