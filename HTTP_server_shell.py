"""
 HTTP Server Shell
 Author: Barak Gonen and Nir Dweck
 Purpose: Provide a basis for Ex. 4
 Note: The code is written in a simple way, without classes, log files or
 other utilities, for educational purpose
 Usage: Fill the missing functions and constants
"""
# TO DO: import modules
import socket
import logging
import re
import os
# TO DO: set constants

QUEUE_SIZE = 10
IP = '0.0.0.0'
PORT = 80
SOCKET_TIMEOUT = 2

# Useful URIs
URI_DEFAULT = '/index.html'
URI_FORBIDDEN = '/forbidden'
URI_MOVED = '/moved'
URI_ERROR = '/error'

# WebRoot paths
WEBROOT = os.path.join(os.path.dirname(__file__), 'webroot')
INDEX = os.path.join(WEBROOT, 'index.html')

# HTTP headers
HEADER_CONTENT_TYPE = b'Content-Type: '
HEADER_CONTENT = b'Content-Length: '

# Content types dictionary
FILE_CONTENT_TYPES = {
    'html': 'text/html;charset=utf-8',
    'jpg': 'image/jpeg',
    'css': 'text/css',
    'js': 'text/javascript; charset=UTF-8',
    'txt': 'text/plain',
    'ico': 'image/x-icon',
    'gif': 'image/jpeg',
    'png': 'image/png'
}

# HTTP status codes
HTTP_OK_200 = b'HTTP/1.1 200 OK\r\n'
HTTP_TEMP_REDIRECT_302 = b'HTTP/1.1 302 TEMPORARY REDIRECT\r\n'
HTTP_FORBIDDEN_403 = b'HTTP/1.1 403 Forbidden\r\n'
HTTP_NOT_FOUND_404 = b'HTTP/1.1 404 Not Found\r\n'
HTTP_INTERNAL_ERROR_505 = b'HTTP/1.1 500 Internal Server Error\r\n'

logging.basicConfig(filename = 'WebRoot_Server_log.log', level = logging.DEBUG)

def get_file_data(file_name):
    """
    Get data from file
    :param file_name: the name of the file
    :return: the file data in a string
    """


def handle_client_request(resource, client_socket):
    """
    Check the required resource, generate proper HTTP response and send
    to client
    :param resource: the required resource
    :param client_socket: a socket for the communication with the client
    :return: None
    """
    """ """
    # TO DO : add code that given a resource (URI and parameters) generates
    # the proper response
    if resource == '':
        uri = URI_DEFAULT
    else:
        uri = resource

    # TO DO: check if URI had been redirected, not available or other error
    # code. For example:
    if uri in REDIRECTION_DICTIONARY:
        pass
        # TO DO: send 302 redirection response

    # TO DO: extract requested file tupe from URL (html, jpg etc)
    if file_type == 'html':
        http_header =  # TO DO: generate proper HTTP header
    elif file_type == 'jpg':
        http_header =  # TO DO: generate proper jpg header
    # TO DO: handle all other headers

    # TO DO: read the data from the file
    data = get_file_data(filename)
    # http_header should be encoded before sended
    # data encoding depends on its content. text should be encoded, while files shouldn't
    http_response = http_header.encode() + data
    client_socket.send(http_response)


def validate_http_request(request):
    """
    Check if request is a valid HTTP request and returns TRUE / FALSE and
    the requested URL
    :param request: the request which was received from the client
    :return: a tuple of (True/False - depending if the request is valid,
    the requested resource )
    """
    # TO DO: write function
    # Is request empty
    ok = True
    method, resource = '', ''
    if request == '':
        ok = False

    valid = re.match(rb'([A-Z]+) + (/.*) + HTTP/1.1', request)

    if valid is None:
        ok = False
    else:
        method = valid.group(1).decode()
        resource = valid.group(2).decode()

        if method != 'GET':
            ok = False

    if ok:
        return True, resource
    else:
        return False, ''





def handle_client(client_socket):
    """
    Handles client requests: verifies client's requests are legal HTTP, calls
    function to handle the requests
    :param client_socket: the socket for the communication with the client
    :return: None
    """
    print('Client connected')
    while True:
        try:

        # TO DO: insert code that receives client request X
        # ...
            client_request = ''
            while b'\r\n\r\n' not in client_request:
                client_request += client_socket.recv(1).decode()

            if client_request == '':
                break

            valid_http, resource = validate_http_request(client_request)

            if valid_http:
                print('Got a valid HTTP request')
                handle_client_request(resource, client_socket)
            else:
                print('Error: Not a valid HTTP request')
                logging.error('Error - invalid HTTP request')
                break
        except socket.timeout:
            logging.debug('Socket connection timed out')
            break
        except socket.error as error:
            logging.error('Socket Error: ' + error)
            break

    print('Closing connection')
    logging.debug('Closing connection')
    client_socket.close()


def main():
    # Open a socket and loop forever while waiting for clients
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((IP, PORT))
        server_socket.listen(QUEUE_SIZE)
        print("Listening for connections on port %d" % PORT)

        while True:
            client_socket, client_address = server_socket.accept()
            try:
                print('New connection received')
                client_socket.settimeout(SOCKET_TIMEOUT)
                handle_client(client_socket)
            except socket.error as err:
                print('received socket exception - ' + str(err))
            finally:
                client_socket.close()
    except socket.error as err:
        print('received socket exception - ' + str(err))
    finally:
        server_socket.close()


if __name__ == "__main__":
    # Call the main handler function
    main()