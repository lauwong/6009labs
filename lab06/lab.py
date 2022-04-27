import sys
from http009 import http_response

import typing
import doctest

sys.setrecursionlimit(10000)

# NO ADDITIONAL IMPORTS!


# custom exception types for lab 6


class HTTPRuntimeError(Exception):
    pass


class HTTPFileNotFoundError(FileNotFoundError):
    pass


# functions for lab 6


def download_file(url, chunk_size=8192, cache={}):
    """
    Yield the raw data from the given URL, in segments of at most chunk_size
    bytes (except when retrieving cached data as seen in section 2.2.1 of the
    writeup, in which cases longer segments can be yielded).

    If the request results in a redirect, yield bytes from the endpoint of the
    redirect.

    If the given URL represents a manifest, yield bytes from the parts
    represented therein, in the order they are specified.

    Raises an HTTPRuntimeError if the URL can't be reached, or in the case of a
    500 status code.  Raises an HTTPFileNotFoundError in the case of a 404
    status code.
    """

    try:
        r = http_response(url)
    except ConnectionError:
        raise HTTPRuntimeError
    else:
        # If the url redirects, keep following the redirects
        while r.status in [301, 302, 307]:
            loc = r.getheader('location')
            r = http_response(loc)

        if r.status == 404:
            raise HTTPFileNotFoundError
        elif r.status == 500:
            raise HTTPRuntimeError

        if ((r.getheader('content-type') == 'text/parts-manifest')
            or (url[-6:] == '.parts')):

            line = None

            while True:
                cacheable = False
                part_urls = []

                while True:
                    # Read each url of a single part and save
                    # to a list of possible urls for the part
                    line = r.readline()

                    if line == b'--\n':
                        break

                    if not line:
                        break

                    if line == b'(*)\n':
                        cacheable = True
                    else:
                        part_urls.append(line.decode('utf-8').strip())

                # If the contents are cacheable, yield the contents of each
                # url, save the full file in a bytestring, and cache
                for loc in part_urls:
                    contents = b''
                    if cacheable:
                        if loc in cache:
                            if cache[loc] == "ERROR":
                                continue
                            else:
                                yield cache[loc]
                                break
                        else:
                            try:
                                for chunk in download_file(loc, cache=cache):
                                    contents += chunk
                                    yield chunk
                            except Exception:
                                # Save the URL as error so it does not retry
                                # later
                                cache[loc] = "ERROR"
                                continue
                            else:
                                cache[loc] = contents
                                break
                    else: # Otherwise, just yield the contents in chunks
                        try:
                            for chunk in download_file(loc):
                                yield chunk
                        except Exception:
                            continue
                        else:
                            break

                if not line:
                    break

        else: # If not a parts manifest, just read the file in chunks and yield
            while True:
                result = r.read(chunk_size)
                if not result:
                    break
                yield result

def files_from_sequence(stream):
    """
    Given a generator from download_file that represents a file sequence, yield
    the files from the sequence in the order they are specified.
    """

    b_arr = bytearray()
    file_len = 0
    files = 0
    end = False

    while True:

        # If the file length marker is too short, add chunks until it is
        # long enough. If there are no more chunks, break out of everything
        while len(b_arr) < 4:
            try:
                b_arr.extend(next(stream))
            except StopIteration:
                end = True
                break

        if end:
            break

        # Get the file length as an integer then delete it from the bytearray
        file_len = int.from_bytes(b_arr[:4], 'big')
        b_arr = b_arr[4:]

        # If the file is not complete, add chunks until the desired length
        # has been reached. If there are no more chunks, yield the current
        # bytearray and break out of everything
        while len(b_arr) < file_len:
            try:
                b_arr.extend(next(stream))
            except StopIteration:
                end = True
                break

        if end:
            break

        # Yield the file and delete it from the bytestring
        yield b_arr[:file_len]
        b_arr = b_arr[file_len:]

def save_file(url, filename):
    """
    Retrieves the full file streamed from a given url and saves it
    to a new file named filename

    If the file is a file sequence, save each file separately following
    the format filename + '-file' + i, where i is the index of the file
    in the sequence
    """
    file_gen = download_file(url)

    name, file_type = filename.split('.')

    if '-seq' in url:
        file_seq = files_from_sequence(file_gen)

        for i, file in enumerate(file_seq):
            with open(name+'-file' + str(i+1) + '.' + file_type, 'wb') as f:
                f.write(file)

    else:
        with open(name + '.' + file_type, 'wb') as f:
            for chunk in file_gen:
                f.write(chunk)


if __name__ == "__main__":

    # If the arguments are found
    if len(sys.argv) > 1:
        url, filename = sys.argv[1:3]
        save_file(url, filename)
