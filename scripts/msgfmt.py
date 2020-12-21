#! /usr/bin/env python3
# Written by Martin v. Löwis <loewis@informatik.hu-berlin.de>

"""Generate binary message catalog from textual translation description.

This program converts a textual Uniforum-style message catalog (.po file) into
a binary GNU catalog (.mo file).  This is essentially the same function as the
GNU msgfmt program, however, it is a simpler implementation.  Currently it
does not handle plural forms but it does handle message contexts.

Usage: msgfmt.py [OPTIONS] filename.po

Options:
    -o file
    --output-file=file
        Specify the output file to write to.  If omitted, output will go to a
        file named filename.mo (based off the input file name).

    -h
    --help
        Print this message and exit.

    -V
    --version
        Display version information and exit.
"""
import argparse
import array
import ast
import os
import struct
import sys
from email.parser import HeaderParser


__version__ = "1.2"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version', version=f'bottex-%(prog)s {__version__}')
    parser.add_argument('-o', '--output-file')
    parser.add_argument('--reversed', action='store_true')
    parser.add_argument('input_file')
    return parser.parse_args()


def swap(messages: dict):
    new = {}
    for key, value in messages.items():
        if key:
            new[value] = key
        else:
            new[key] = value
    return new


def po_filename(filename):
    if filename.endswith('.po'):
        return filename
    else:
        return filename + '.po'


def mo_filename(po_fn):
    return os.path.splitext(po_fn)[0] + '.mo'


def readlines(filename):
    try:
        with open(filename, 'rb') as f:
            return f.readlines()
    except IOError as msg:
        print(msg, file=sys.stderr)
        sys.exit(1)


def write(filename, binary):
    try:
        with open(filename, 'wb') as f:
            f.write(binary)
    except IOError as msg:
        print(msg, file=sys.stderr)


# noinspection PyUnboundLocalVariable
def parse(lines):
    messages = {}

    def add(ctxt_, id_, str_, fuzzy_):
        """Add a non-fuzzy translation to the dictionary."""
        if not fuzzy_ and str_:
            if ctxt_ is None:
                messages[id_] = str_
            else:
                messages[b"%b\x04%b" % (ctxt_, id_)] = str_

    ID = 1
    STR = 2
    CTXT = 3

    section = msgctxt = None
    fuzzy = 0

    # Start off assuming Latin-1, so everything decodes without failure,
    # until we know the exact encoding
    encoding = 'latin-1'

    # Parse the catalog
    lno = 0
    for l in lines:
        l = l.decode(encoding)
        lno += 1
        # If we get a comment line after a msgstr, this is a new entry
        if l[0] == '#' and section == STR:
            add(msgctxt, msgid, msgstr, fuzzy)
            section = msgctxt = None
            fuzzy = 0
        # Record a fuzzy mark
        if l[:2] == '#,' and 'fuzzy' in l:
            fuzzy = 1
        # Skip comments
        if l[0] == '#':
            continue
        # Now we are in a msgid or msgctxt section, output previous section
        if l.startswith('msgctxt'):
            if section == STR:
                add(msgctxt, msgid, msgstr, fuzzy)
            section = CTXT
            l = l[7:]
            msgctxt = b''
        elif l.startswith('msgid') and not l.startswith('msgid_plural'):
            if section == STR:
                add(msgctxt, msgid, msgstr, fuzzy)
                if not msgid:
                    # See whether there is an encoding declaration
                    p = HeaderParser()
                    charset = p.parsestr(msgstr.decode(encoding)).get_content_charset()
                    if charset:
                        encoding = charset
            section = ID
            l = l[5:]
            msgid = msgstr = b''
            is_plural = False
        # This is a message with plural forms
        elif l.startswith('msgid_plural'):
            if section != ID:
                print('msgid_plural not preceded by msgid on %d' % lno,
                      file=sys.stderr)
                sys.exit(1)
            l = l[12:]
            msgid += b'\0'  # separator of singular and plural
            is_plural = True
        # Now we are in a msgstr section
        elif l.startswith('msgstr'):
            section = STR
            if l.startswith('msgstr['):
                if not is_plural:
                    print('plural without msgid_plural on %d' % lno,
                          file=sys.stderr)
                    sys.exit(1)
                l = l.split(']', 1)[1]
                if msgstr:
                    msgstr += b'\0'  # Separator of the various plural forms
            else:
                if is_plural:
                    print('indexed msgstr required for plural on %d' % lno,
                          file=sys.stderr)
                    sys.exit(1)
                l = l[6:]
        # Skip empty lines
        l = l.strip()
        if not l:
            continue
        l = ast.literal_eval(l)
        if section == CTXT:
            msgctxt += l.encode(encoding)
        elif section == ID:
            msgid += l.encode(encoding)
        elif section == STR:
            msgstr += l.encode(encoding)
        else:
            print('Syntax error on %d' % lno,
                  'before:', file=sys.stderr)
            print(l, file=sys.stderr)
            sys.exit(1)
    # Add last entry
    if section == STR:
        add(msgctxt, msgid, msgstr, fuzzy)
    return messages


def generate(messages):
    """Return the generated output."""
    # the keys are sorted in the .mo file
    keys = sorted(messages.keys())
    offsets = []
    ids = strs = b''
    for id_ in keys:
        # For each string, we need size and file offset.  Each string is NUL
        # terminated; the NUL does not count into the size.
        offsets.append((len(ids), len(id_), len(strs), len(messages[id_])))
        ids += id_ + b'\0'
        strs += messages[id_] + b'\0'
    output = ''
    # The header is 7 32-bit unsigned integers.  We don't use hash tables, so
    # the keys start right after the index tables.
    # translated string.
    keystart = 7*4+16*len(keys)
    # and the values start after the keys
    valuestart = keystart + len(ids)
    koffsets = []
    voffsets = []
    # The string table first has the list of keys, then the list of values.
    # Each entry has first the size of the string, then the file offset.
    for o1, l1, o2, l2 in offsets:
        koffsets += [l1, o1+keystart]
        voffsets += [l2, o2+valuestart]
    offsets = koffsets + voffsets
    output = struct.pack("Iiiiiii",
                         0x950412de,       # Magic
                         0,                 # Version
                         len(keys),         # # of entries
                         7*4,               # start of key index
                         7*4+len(keys)*8,   # start of value index
                         0, 0)              # size and offset of hash table
    output += array.array("i", offsets).tobytes()
    output += ids
    output += strs
    return output


def main():
    args = parse_args()

    infile = po_filename(args.input_file)
    if args.output_file is None:
        args.output_file = mo_filename(infile)

    lines = readlines(infile)
    messages = parse(lines)
    binary = generate(messages)
    write(args.output_file, binary)

    if args.reversed:
        # if reversed_filename is None:
        dirname = os.path.dirname(infile)
        reversed_filename = os.path.join(dirname, 'reversed.mo')
        swapped = swap(messages)
        reversed_binary = generate(swapped)
        write(reversed_filename, reversed_binary)


if __name__ == '__main__':
    main()
