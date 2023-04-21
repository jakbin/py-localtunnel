import argparse
from py_localtunnel.tunnel import Tunnel

__version__ = "1.0.1"
package_name = "pylt"

example_uses = '''example:
   pylt port {port_number}'''

def main(argv = None):
    parser = argparse.ArgumentParser(prog=package_name, description="localtunnel alternative in python", epilog=example_uses, formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers(dest="command")

    port_parser = subparsers.add_parser('port', help="Internal HTTP server port")
    port_parser.add_argument('port', type=int, help="Internal HTTP server port")
    port_parser.add_argument('-s', '--subdomain', type=str, default="", help="Request this subdomain")

    parser.add_argument('-v',"--version", action="store_true", dest="version", help="check version of deb")

    args = parser.parse_args(argv)

    if args.command == "port":
        t = Tunnel()
        url = t.get_url(args.subdomain)
        print(f" your url is: {url}")
        try:
            t.create_tunnel(args.port)
        except KeyboardInterrupt:
            print("KeyboardInterrupt: stopping tunnel")

        t.stop_tunnel()

    elif args.version:
        return print(__version__)
    else:
        parser.print_help()

if __name__ == '__main__':
    raise SystemExit(main())
