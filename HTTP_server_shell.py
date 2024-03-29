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
WEBROOT = r'C:\Users\tomer\Desktop\Python_Projects\WebRoot4.0\webroot.zip'
INDEX = os.path.join(WEBROOT, 'index.html')

# Images paths
ERROR_IMAGE_PATH = os.path.join(os.path.dirname(__file__), 'images', 'error.jpg')
FORBIDDEN_IMAGE_PATH = os.path.join(os.path.dirname(__file__), 'images', 'forbidden.jpg')
NOT_FOUND__IMAGE_PATH = os.path.join(os.path.dirname(__file__), 'images', 'notFound.jpg')

# HTTP headers
HEADER_CONTENT_TYPE = b'Content-Type: '
HEADER_CONTENT_LENGTH = b'Content-Length: '

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
HTTP_INTERNAL_ERROR_500 = b'HTTP/1.1 500 Internal Server Error\r\n'

logging.basicConfig(filename='WebRoot_Server_log.log', level=logging.DEBUG)


def get_file_data(file_path):
    """
    Get data from file
    :param file_path: the path of the intended file
    :return: the file data in a string and the len of the data
    """
    with open(file_path, 'rb') as file:
        file_data = file.read()
        file_content_len = len(file_data)
    return file_data, file_content_len


def handle_client_request(resource, client_socket):
    """
    Check the required resource, generate proper HTTP response and send
    to client
    :param resource: the required resource
    :param client_socket: a socket for the communication with the client
    :return: None
    """
    logging.debug("Handling client request: " + resource)
    if resource == '' or resource == '/':
        uri = URI_DEFAULT
    else:
        uri = resource

    try:
        if uri == URI_MOVED:
            logging.debug('URI Moved has been requested')
            response = HTTP_TEMP_REDIRECT_302 + b'Location: /index.html\r\n\r\n'
            client_socket.sendall(response)
            handle_client_request('/', client_socket)
            return
        elif uri == URI_FORBIDDEN:
            logging.debug('URI Forbidden has been requested')
            image_data, image_content_len = get_file_data(FORBIDDEN_IMAGE_PATH)
            image_content_type_header = HEADER_CONTENT_TYPE + FILE_CONTENT_TYPES.get('jpg', b'image/jpeg').encode() + b'\r\n'
            image_content_len_header = HEADER_CONTENT_LENGTH + str(image_content_len).encode() + b'\r\n'
            image_final = HTTP_FORBIDDEN_403 + image_content_type_header + image_content_len_header + b'\r\n' + image_data
            client_socket.sendall(image_final)
        elif uri == URI_ERROR:
            logging.debug('URI Error has been requested')
            image_data, image_content_len = get_file_data(ERROR_IMAGE_PATH)
            image_content_type_header = HEADER_CONTENT_TYPE + FILE_CONTENT_TYPES.get('jpg', b'image/jpeg').encode() + b'\r\n'
            image_content_len_header = HEADER_CONTENT_LENGTH + str(image_content_len).encode() + b'\r\n'
            image_final = HTTP_INTERNAL_ERROR_500 + image_content_type_header + image_content_len_header + b'\r\n' + image_data
            client_socket.sendall(image_final)
        else:
            filename = os.path.join(WEBROOT, uri.strip('/'))
            if os.path.isdir(filename):
                filename = os.path.join(filename, 'index.html')
            file_extension = filename.split('.')[-1]

            file_data, data_len = get_file_data(filename)
            content_type_header = HEADER_CONTENT_TYPE + FILE_CONTENT_TYPES.get(file_extension, b'text/plain').encode() + b'\r\n'
            content_len_header = HEADER_CONTENT_LENGTH + str(data_len).encode() + b'\r\n'
            final_response = HTTP_OK_200 + content_type_header + content_len_header + b'\r\n' + file_data
            client_socket.sendall(final_response)
    except FileNotFoundError:
        logging.debug('Not Found error occurred')
        image_data, image_content_len = get_file_data(NOT_FOUND__IMAGE_PATH)
        image_content_type_header = HEADER_CONTENT_TYPE + FILE_CONTENT_TYPES.get('jpg', b'image/jpeg').encode() + b'\r\n'
        image_content_len_header = HEADER_CONTENT_LENGTH + str(image_content_len).encode() + b'\r\n'
        image_final = HTTP_NOT_FOUND_404 + image_content_type_header + image_content_len_header + b'\r\n' + image_data
        client_socket.sendall(image_final)
    except Exception:
        logging.debug('Internal Error error occurred')
        image_data, image_content_len = get_file_data(ERROR_IMAGE_PATH)
        image_content_type_header = HEADER_CONTENT_TYPE + FILE_CONTENT_TYPES.get('jpg', b'image/jpeg').encode() + b'\r\n'
        image_content_len_header = HEADER_CONTENT_LENGTH + str(image_content_len).encode() + b'\r\n'
        image_final = HTTP_INTERNAL_ERROR_500 + image_content_type_header + image_content_len_header + b'\r\n' + image_data
        client_socket.sendall(image_final)


def validate_http_request(request):
    """
    Check if request is a valid HTTP request and returns TRUE / FALSE and
    the requested URL
    :param request: the request which was received from the client
    :return: a tuple of (True/False - depending if the request is valid,
    the requested resource )
    """
    method, resource = '', ''
    if not request:
        return False, ''

    valid = re.match(rb'([A-Z]+) +(/.*) +HTTP/1.1', request)

    if not valid:
        return False, ''
    else:
        method = valid.group(1).decode()
        resource = valid.group(2).decode()

        if method != 'GET':
            return False, ''

    return True, resource


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
            client_request = b''
            while b'\r\n\r\n' not in client_request:
                client_request += client_socket.recv(1)

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
            logging.error('Socket Error')
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
