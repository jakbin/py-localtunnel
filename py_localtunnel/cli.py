import argparse
from py_localtunnel.lt import run_localtunnel

__version__ = "1.0.3"
package_name = "pylt"

example_uses = '''example:
   pylt port {port_number}
   pylt port {port_number} -s {your_custom_subdomain}'''

def main(argv = None):
    parser = argparse.ArgumentParser(prog=package_name, description="localtunnel alternative in python", epilog=example_uses, formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers(dest="command")

    port_parser = subparsers.add_parser('port', help="Internal HTTP server port")
    port_parser.add_argument('port', type=int, help="Internal HTTP server port")
    port_parser.add_argument('-s', '--subdomain', type=str, default="", help="Request this subdomain")
    port_parser.add_argument('-lh', '--local-host', type=str, default="localhost", help="Proxy to this hostname instead of `localhost`")

    parser.add_argument('-v',"--version", action="store_true", dest="version", help="check version of deb")

    args = parser.parse_args(argv)

    if args.command == "port":
        run_localtunnel(args.port, args.subdomain, args.local_host)
    elif args.version:
        return print(__version__)
    else:
        parser.print_help()

if __name__ == '__main__':
    raise SystemExit(main())
