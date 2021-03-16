import ROOT as r
import yaml
import json
import argparse

def parse_cli():
    parser = argparse.ArgumentParser(prog='Text dump of nuisance pulls.')
    parser.add_argument(
                        'fitfile',
                        type=str,
                        help='Output file from FitDiagnostics'
                        )
    parser.add_argument(
                        '--format',
                        type=str,
                        help='Output format',
                        default='json',
                        choices=['json','yaml']
                        )

    args = parser.parse_args()

    return args



def get_nuisance_dict(args):
    """Extract nuisance values from RooFitResult in input file"""
    f = r.TFile(args.fitfile)

    nuisance_dict = {}
    for fit in "fit_b","fit_s":
        nuisance_dict[fit] = []
        params = f.Get(fit).floatParsFinal()


        for i in range(params.getSize()):
            p = params.at(i)
            nuisance_dict[fit].append(
                {
                    "name"  : p.GetName(),
                    "value" : p.getVal(),
                    "error" : p.getError()
                }
            )
    return nuisance_dict


def save_nuisance_dict(nuisance_dict, args):
    """Save dict to disk, format depends on args"""
    outfile = args.fitfile.replace(".root","." + args.format)

    if args.format=='json':
        payload = json.dumps(nuisance_dict,indent=4)
    elif args.format=='yaml':
        payload = yaml.dump(nuisance_dict, indent=4)
    else:
        raise RuntimeError("Invalid format name: " + args.format)
    with open(outfile, "w") as f:
        f.write(payload)



def main():
    args = parse_cli()
    nuisance_dict = get_nuisance_dict(args)
    save_nuisance_dict(nuisance_dict, args)

if __name__ == "__main__":
    main()
