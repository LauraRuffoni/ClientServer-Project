import socket  # Import socket module
import argparse  # Import socket module


class Errore(Exception):
    pass


def verbose0(msg, outfile):
    # in case of wrong sequences print corresponding header
    if msg.startswith("%%%"):

        # divide headers containing errors from the correct output
        msg = msg.split("\n", 1)

        # create and write output file
        with open(outfile, "w") as file:
            file.write(msg[1])

    # code for completely correct input file
    elif msg.startswith(">") or msg.startswith("<"):

        # create and write output file
        with open(outfile, "w") as file:
            file.write(msg)

    # code for not acceptable input file
    else:
        print(msg)


def verbose1(msg, outfile):
    # in case of wrong sequences print corresponding header
    if msg.startswith("%%%"):

        c = msg.count("<") + msg.count(">")

        # divide headers containing errors from the correct output
        msg = msg.split("\n", 1)

        # create and write output file
        with open(outfile, "w") as file:
            file.write(msg[1])

        # extract headers where errors were found in the Server
        errorHeaders = [line for line in msg[0].split("%%%") if line != ""]

        # prepare verbose output
        text_output = f"{outfile} created with {c - len(errorHeaders)} out of {c} total inputs."
        print(text_output)

    # code for completely correct input file
    elif msg.startswith(">") or msg.startswith("<"):

        c = msg.count("<") + msg.count(">")

        # create and write output file
        with open(outfile, "w") as file:
            file.write(msg)

        print(f"{outfile} correctly created with a total of {c} transformation.")

    # code for not acceptable input file
    else:
        print(msg)


def verbose2(msg, outfile):

    # in case of wrong sequences print corresponding header
    if msg.startswith("%%%"):

        c = msg.count("<") + msg.count(">")

        # divide headers containing errors from the correct output
        msg = msg.split("\n", 1)

        # create and write output file
        with open(outfile, "w") as file:
            file.write(msg[1])

        # extract headers where errors were found in the Server
        errorHeaders = [line for line in msg[0].split("%%%") if line != ""]

        # prepare verbose output
        text_output = (f"{outfile} created with {c-len(errorHeaders)} out of {c} total inputs.\n"
                       f"Skipped {len(errorHeaders)} inputs:\n")

        if len(errorHeaders) > 1:
            text_output += "\n".join(errorHeaders)
        else:
            text_output += errorHeaders[0]
        print(text_output)

    # code for completely correct input file
    elif msg.startswith(">") or msg.startswith("<"):

        c = msg.count("<") + msg.count(">")

        # create and write output file
        with open(outfile, "w") as file:
            file.write(msg)

        print(f"{outfile} correctly created with a total of {c} transformation.")

    # code for not acceptable input file
    else:
        print(msg)


def client_connect(host, port, inputfile, outfile, verbosity):
    # Active opening
    # Creates socket and makes connection to the Server.
    s = socket.socket()
    try:
        s.connect((host, port))
    except OverflowError:
        print("Port not valid, please enter an integer between 1 and 65535")
        exit()
    except socket.gaierror:
        print("Address not valid, please enter valid hostname or IP address")
        exit()

    # Checks if input file is text file, if not sends its content to Server
    try:
        with open(inputfile, "r") as inpfile:
            content = inpfile.read()
    except Errore:
        print("Error reading, input file not .txt or .fasta")
        exit()
    except FileNotFoundError:
        print("File not found, please enter a valid input file")
        exit()
    s.sendall(content.encode() + b"/0")

    # receives all output from Server.
    msg = b""
    end = b"/0"
    while True:
        msg += s.recv(1024)
        if end in msg:
            break
    msg = msg.decode().replace(end.decode(), "")

    # Creates outputfile with transformed sequences:
    if verbosity == 0:
        verbose0(msg, outfile)
    elif verbosity == 1:
        verbose1(msg, outfile)
    elif verbosity == 2:
        verbose2(msg, outfile)

    # Close connection
    s.close()


def main():
    # description of program
    parser = argparse.ArgumentParser(description='Project 5: BWT client and server\nInstructions for CLIENT.py',
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     epilog="Author: Laura Ruffoni")

    # Positional arguments:
    # input file name
    parser.add_argument("InputFile", help="Input files should be in either .txt or .fasta format and may "
                                          "contain one or more sequences.\nEach sequence entry must consist of a header"
                                          " and its corresponding sequence, with the header being on a single line and "
                                          "beginning with a specific symbol:\n\"<\" for BWT sequences or \">\" for DNA "
                                          "sequences.\nBlank lines are permitted, but sequences must consist only of "
                                          "DNA characters without digits or whitespace.\nBWT termination symbol must "
                                          "be only one $.")

    # Optional arguments:
    # socket's data for connection, if missing default options available
    parser.add_argument("-a", dest="addr", metavar="Address", default=socket.gethostname(),
                        help="Specify the IP address of the server.\n"
                             "Defaults to the IP address of the current machine.")
    parser.add_argument("-p", dest="port", metavar="Port", type=int, default=5500,
                        help="Specify the port number of the server to be contacted.\nDefaults to port 5057.")

    # output file name, if missing default name: "output.txt"
    parser.add_argument("-o", dest="outfile", metavar="OutputFile", default="output.txt", help="Output file"
                                                                                               " name, by default, is "
                                                                                               "'output.txt'.\nIt will "
                                                                                               "contain DNA sequences "
                                                                                               "transformed into BWT "
                                                                                               "format, with the header"
                                                                                               " symbol changed from "
                                                                                               "'>' to '<', and vice "
                                                                                               "versa for the reverse "
                                                                                               "transformation.")

    # verbose option
    parser.add_argument("-v", dest="verbose", choices=[0, 1, 2], default=1, type=int, help="Verbose level option.\n"
                                                                                           "- 0: Output file created "
                                                                                           "without additional "
                                                                                           "information.\n"
                                                                                           "- 1: Explicit number of "
                                                                                           "transformations included "
                                                                                           "in the output file, along "
                                                                                           "with a summary in the "
                                                                                           "terminal.\n"
                                                                                           "- 2: Explicit headers "
                                                                                           "indicated where an error "
                                                                                           "is found, with details "
                                                                                           "printed in the terminal.\n")

    args = parser.parse_args()

    # function for creating connection and sending input file
    client_connect(args.addr, args.port, args.InputFile, args.outfile, args.verbose)


if __name__ == "__main__":
    main()
