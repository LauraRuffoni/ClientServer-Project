import socket
import multiprocessing
import argparse
import numpy as np


class Errore(Exception):
    pass


def validate_input(seq):
    """
    Validates if the input is a valid DNA sequence.
    :param seq: The DNA sequence to validate as a string.
    :return: True if the sequence is valid, False otherwise.
    """

    validDNA = ["A", "C", "G", "T", "R", "Y", "S", "W", "K", "M", "B", "D", "H", "V", "N", "-"]
    seq = seq.replace("$", "")

    # error is raised if invalid or no sequence found after header
    try:
        if len(seq) == 0 or (not all(nucl.upper() in validDNA for nucl in seq)):
            raise Errore
    except Errore:
        return False
    else:
        return True


def DNAtoBWT(word):
    """
    Transforms the original DNA sequence to the Burrows-Wheeler Transform (BWT).

    :param word: The original DNA sequence as a string.
    :return: The BWT of the DNA sequence as a string.
    """

    arr_perm = np.empty((len(word)), dtype=object)

    # create all permutation by rotating N=(length of input sequence) times
    for i in range(len(word)):
        word = word[-1] + word[:(len(word) - 1)]
        arr_perm[i] = word

    # sort permutation in lexicographic order
    arr_perm = np.sort(arr_perm)

    # extract last column --> all last characters or ordered permutations
    last = np.empty((len(word)), dtype=object)

    for i in range(len(word)):
        last[i] = arr_perm[i][-1]
    last = "".join(last)

    return last


def BWTtoDNA(word):
    """
    Performs the inverse transformation from BWT sequence to the original DNA sequence.

    :param word: The BWT sequence as a string.
    :return: The original DNA sequence as a string.
    """

    word = np.array(list(word), dtype=object)

    # extract first column of all ordered permutations --> the list of character each permutation begins
    sort_word = np.sort(word)

    # re-built all permutations of original DNA
    while len(sort_word) > len(sort_word[0]):
        sort_word = word + sort_word
        sort_word = np.sort(sort_word)

    # original sequence is the one where termination symbol is the last
    res = [perm for perm in sort_word if perm[-1] == "$"][0]

    return res


def checkAndTranslate(msg):
    """
    Checks the correctness of the input file, parses it, and creates the output.

    :param msg: The input message as a string.
    :return: A tuple containing a list of error headers and a list of output lines.
    """

    # each line is in list
    lines = [line for line in msg.split("\n") if line != ""]

    # add termination character
    lines.append("<")

    error_headers = []
    out = []

    # check if input file is not empty or just header, and if the first line is a header
    if len(lines) < 3 or not (lines[0].startswith(">") or lines[0].startswith("<")):
        return False

    elem = ""
    header = "%%%"

    # parsing input file
    for i in range(0, len(lines)):

        # check if current line is a header, otherwise collects following sequence
        if lines[i].startswith(">") or lines[i].startswith("<"):

            # sequence check
            if not validate_input(elem) and i > 0:
                error_headers.append(header)

            # if sequence is DNA, its transformation is performed
            elif header.startswith(">"):
                out.append("< " + header[1:])
                out.append(DNAtoBWT(elem + "$"))

            # if sequence is BWT, its inverse is performed
            elif header.startswith("<"):
                out.append("> " + header[1:])
                out.append(BWTtoDNA(elem))

            # new header found
            elem = ""
            header = lines[i]

        else:
            elem += lines[i].strip("\n")

    return error_headers, out


def output_manager(error_headers, out):
    """
    Generates the output file content.

    :param error_headers: List of headers where errors were found.
    :param out: List of output lines.
    :return: The final output as a string.
    """

    final = ""

    # if skipped headers, special symbol added to distinguish them in Client
    if len(error_headers) > 0:
        final += "%%%" + "%%%".join(error_headers) + "\n"

    final += "\n".join(out)

    return final


def handle_client(conn, addr):
    """
    Handle client connections, receives the input, processes it, and sends back the output.

    :param conn: The connection object.
    :param addr: The address of the client.
    """
    print('Got connection from', addr)

    # Receive input form Client
    msg = b""
    end = b"/0"
    while True:
        msg += conn.recv(1024)
        if end in msg:
            break  # If no more data is received, break the loop
    msg = msg.decode().replace(end.decode(), "")   # remove termination symbol

    # function to check, parse and transformation
    result = checkAndTranslate(msg)

    # creates output
    if result:
        output = output_manager(result[0], result[1])
    else:
        output = "Input Error: either empty file or no header in first line"

    # sends output to Client
    conn.sendall(output.encode() + b"/0")

    # close connection
    conn.close()


def server_main(host, port):
    """
    Start the server, listen for connections, and spawn a process for each client.

    :param host: The hostname or IP address to bind the server.
    :param port: The port number to bind the server.
    """
    # Passive opening
    s = socket.socket()
    try:
        s.bind((host, port))
    except OverflowError:
        print("Port not valid, please enter an integer between 1 and 65535")
        exit()
    else:
        print(f"Listening on address {host} and port {port}")
        s.listen()


    while True:
        # accepting client connections
        conn, addr = s.accept()

        # Create process for each client connecting
        client_process = multiprocessing.Process(target=handle_client, args=(conn, addr))
        client_process.daemon = True
        client_process.start()


def main():
    """
    Parse command-line arguments and start the server.
    """
    parser = argparse.ArgumentParser(description='Project 5: BWT client and server\nInstructions for SERVER.py',
                                     formatter_class=argparse.RawTextHelpFormatter)

    # Optional arguments:
    # socket's data for connection, if missing default options available
    addr = socket.gethostname()

    parser.add_argument('-p', dest="port", metavar='Port', type=int, default=5500,
                        help="Specify the port number of the server to be contacted.\nDefaults to port 5500.")

    args = parser.parse_args()

    # function for starting socket and listening mode
    server_main(addr, args.port)


if __name__ == "__main__":
    main()
