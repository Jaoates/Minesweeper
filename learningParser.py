import argparse

parser = argparse.ArgumentParser(description='Intake some optional args.')
# parser.add_argument('integers', metavar='N', type=int, nargs='+',
#                     help='an integer for the accumulator')
parser.add_argument('--large', dest='size', action='store_const',
                    const="large", default="medium",
                    help='large board (default: medium)')
parser.add_argument('--small', dest='size', action='store_const',
                    const="small", default="medium",
                    help='small board (default: medium)')
parser.add_argument('--medium', dest='size', action='store_const',
                    const="medium", default="medium",
                    help='medium board (default: medium)')


parser.add_argument('--hard', dest='difficulty', action='store_const',
                    const="hard", default="hard",
                    help='hard difficulty (default: moderate)')
parser.add_argument('--easy', dest='difficulty', action='store_const',
                    const="easy", default="moderate",
                    help='easy difficulty (default: moderate)')
parser.add_argument('--moderate', dest='difficulty', action='store_const',
                    const="moderate", default="hard",
                    help='moderate difficulty (default: moderate)')

args = parser.parse_args()
boardSize = {
    "small":[10,5],
    "medium":[20,10],
    "large":[40,15]
}[args.size]

boardSize = {
    "small":.3,
    "medium":.4,
    "large":.5
}[args.size]
