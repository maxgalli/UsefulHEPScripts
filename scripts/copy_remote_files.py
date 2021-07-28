import argparse
import os
import json
import subprocess


def json_str(obj):
    return json.dumps(obj, sort_keys=True, indent=4)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Given a JSON file as input, copy the remote files locally")

    parser.add_argument(
            "-i",
            "--input",
            help="JSON file with paths to remote datasets",
            required=True
            )

    parser.add_argument(
            "-o",
            "--output",
            help="Output directory for the copied files",
            default="."
            )

    return parser.parse_args()


def main(args):
    input_json = args.input
    output_dir = args.output

    with open(input_json, ) as f:
        info = json.load(f)

    cmd = "xrdcp"

    processes = []
    # Loop over info and copy files with xrdcp
    for dataset_name, files in info.items():
        for remote_fl in files:
            local_file = remote_fl.split("/")[-1]
            full_output_file = "/".join([output_dir, dataset_name, local_file])
            if os.path.exists(full_output_file):
                print("Skipping {}/{} as it already exists".format(dataset_name, local_file))
            else:
                processes.append(
                        subprocess.Popen([cmd, remote_fl, full_output_file])
                        )

    if processes:
        # wait for all subprocesses to finish
        exit_codes = [sp.wait() for sp in processes]

        if all(ec == 0 for ec in exit_codes):
            print("All processes completed succesfully")
        else:
            for ec in exit_codes:
                if ec != 0:
                    print("Failed: {}".format(ec))
    else:
        print("No operation performed as all the files were already there")



if __name__ == "__main__":
    args = parse_arguments()
    main(args)
