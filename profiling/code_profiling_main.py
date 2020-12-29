import argparse
import code_profiling


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dim", type=int, required=True)
    parser.add_argument("--loops", type=int, required=True)

    return parser.parse_args()


def main(args):
    dim = args.dim
    loops = args.loops

    lst = code_profiling.random_array_for_loop(dim, loops)


if __name__ == '__main__':
    args = parse_arguments()
    main(args)
