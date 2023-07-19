from __future__ import annotations
import io
import os


def readlines_with_Fn(path: str, fn=None, merge_with=None, stripchars="\n\r", enc='utf-8', verbose=False):
    """read something line by line, applying predicate to every line. ReturnsModified lines;"""
    ###Can read gibberish replacing broken chars with ?, unrecoverable lines reported in ./error.log
    if not os.path.isfile(path):
        raise ValueError(f"Expected file at {path}. Failed to fetch.")
    predicate = bool(fn)
    res_l = merge_with if merge_with else []
    with io.open(path, encoding=enc, errors='replace') as fh:
        try:
            while True:
                line = fh.readline()
                if not line:
                    break
                if stripchars != "":
                    line = line.strip(stripchars)
                res = fn(line) if predicate else line
                res_l.append(res)
        except UnicodeDecodeError as e:
            if verbose:
                print(f"Error with decoding {path}")
                print(e)
            with open("./error.log", "at") as efh:
                efh.writelines([path, str(e), '\r\n'])
    return res_l


def reverse_readline(path: str, buf_size=8192, split_char='\n'):
    """A generator that returns the lines of a file in reverse order"""
    ###Most of the time we work with insanly big files, seeking stuff from the end of the file
    ###TODO doesn't work propertly with escaped '\n's, implement look-back-regexp?
    if not os.path.isfile(path):
        raise ValueError(f"Expected file at {path}. Failed to fetch.")
    with open(path) as fh:
        segment = None
        offset = 0
        fh.seek(0, os.SEEK_END)
        file_size = remaining_size = fh.tell()
        while remaining_size > 0:
            offset = min(file_size, offset + buf_size)
            fh.seek(file_size - offset)
            buffer = fh.read(min(remaining_size, buf_size))
            remaining_size -= buf_size
            lines = buffer.split(split_char)
            if segment is not None:
                # If the previous chunk starts right from the beginning of line
                # do not concat the segment to the last line of new chunk.
                # Instead, yield the segment first
                if buffer[-1] != split_char:
                    lines[-1] += segment
                else:
                    yield segment
            segment = lines[0]
            for index in range(len(lines) - 1, 0, -1):
                if lines[index]:
                    yield lines[index]
        if segment is not None:
            yield segment


def reverse_racing_readline_wrappers(path: str, buf_size=8192, split_char='\n', fn=None, pred=None):
    """A generator that returns the lines of a file in reverse order
    fn: runnable - decorator, which contains all runnables to apply before returning segment
    pred: runnable -> bool, filter
    """
    ###TODO doesn't work propertly with escaped '\n's, implement look-back-regexp?
    if not os.path.isfile(path):
        raise ValueError(f"Expected file at {path}. Failed to fetch.")
    with open(path) as fh:
        segment = None
        offset = 0
        fh.seek(0, os.SEEK_END)
        file_size = remaining_size = fh.tell()
        while remaining_size > 0:
            offset = min(file_size, offset + buf_size)
            fh.seek(file_size - offset)
            buffer = fh.read(min(remaining_size, buf_size))
            remaining_size -= buf_size
            lines = buffer.split(split_char)
            if segment is not None:
                if buffer[-1] != split_char:
                    lines[-1] += segment
                else:
                    yield segment
            segment = lines[0]
            for index in range(len(lines) - 1, 0, -1):
                if lines[index]:
                    yield lines[index]
            if file_size != fh.tell:
                raise ValueError("Too slow, file changed")

        if pred is not None:
            if not pred(segment):
                yield from reverse_racing_readline_wrappers(path, buf_size, split_char, fn, pred)
        if segment is not None:
            if fn is not None:
                yield fn(segment)
            else:
                yield segment


def traverse_log_to_ts(path: str, ts):
    """Read text IUM log from the end, until in ts in log is bigger then provided ts"""
    ...
