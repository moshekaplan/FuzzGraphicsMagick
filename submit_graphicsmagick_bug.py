#!/usr/bin/env python

"""\
Script for submitting GraphicsMagick bugs
Attempts to convert a file with GraphicsMagick. If the file crashes GraphicsMagick,
the script creates a new issue on SourceForge with the crash output and file.
"""

import sys
import base64
import subprocess

import requests

# From https://sourceforge.net/auth/oauth/
# Account-specific values:
SOURCEFORGE_TOKEN  = "REDACTED"

# System-specific values:
GRAPHICSMAGICK_DIR = "/home/user/Desktop/FuzzGraphicsMagick/graphicsmagick"
GRAPHICSMAGICK_BIN = "/home/user/Desktop/FuzzGraphicsMagick/graphicsmagick/utilities/gm"

# Target-specific values:
SOURCEFORGE_URL = "https://sourceforge.net/rest/p/graphicsmagick/bugs/new"
bug_description_header = "This bug was found while fuzzing graphicsmagick with afl-fuzz\n\n"
bug_description_version = "Tested on hg changeset %s\n\n"
bug_description_command = "Command: gm convert %s /dev/null\n\n"


def get_hg_commit():
    cmd = "cd %s && hg identify --id" % GRAPHICSMAGICK_DIR
    proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    return out


def submit_bug_report(title, body, filename):
    url = SOURCEFORGE_URL + "?access_token=" + SOURCEFORGE_TOKEN

    with open(filename, 'rb') as fh:
        filecontents = fh.read()

    body = {'access_token':SOURCEFORGE_TOKEN,
        'ticket_form.description': body,
        'ticket_form.summary':title,
        }

    files={'ticket_form.attachment':(filename, filecontents, "application/octet-stream")}
    r = requests.post(url, data=body, files=files)


def parse_asan_output(output):
    lines = [line.strip() for line in output.split('\n')]
#    for line in lines:
#        print line
    
    print lines[0]
    return
    # Memory allocation errors are boring
    if "ERROR: AddressSanitizer failed to allocate" in output:
        "overly-large call to malloc failed; skipped"
        return
    try:
        err_location_line = [line for line in output.split('\n') if 'graphicsmagick' in line][0]
        err_location = err_location_line.split("graphicsmagick/", 1)[1]

        err_info_line = [line for line in output.split('\n') if 'ERROR: AddressSanitizer:' in line][0]
        err_type = err_info_line.split("ERROR: AddressSanitizer: ", 1)[1].split(' ', 1)[0]
    except Exception, e:
        print "error processing output"
        print e
        return


def test_file(filename):
    cmd = GRAPHICSMAGICK_BIN + ' convert "%s" /dev/null' % filename
    print "running: " + cmd
    proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    #print "program output:"
    #print err
    return err


def submit_bug(filename, output):


    bug_filename = filename.rsplit('/', 1)[-1]

    if "WRITE of size" in output:
        err_type = "out-of-bounds write"
    if "READ of size" in output:
        err_type = "out-of-bounds read"

    bug_title = "%s in %s" % (err_type, err_location)

    hg_commit = get_hg_commit()
    if not hg_commit:
        hg_commit = "<unknown>"

    bug_description = bug_description_header + (bug_description_version % hg_commit) + (bug_description_command % bug_filename) + output
    bug_comment = "input file to trigger crash"

    print bug_title

    submit = raw_input("Submit bug?\n")
    if submit.lower()[0] != "y":
        print "Skipped"
        return
    
    submit_bug_report(bug_title, bug_description, bug_filename)


def main():
    if len(sys.argv) < 2:
        print "USAGE: python %s filename" % (sys.argv[0])
        sys.exit(1)

    filename = sys.argv[1]
    output = test_file(filename)
    
    if output:
        parse_asan_output(output)
        #submit_bug(filename, output)


if __name__ == '__main__':
    main()

