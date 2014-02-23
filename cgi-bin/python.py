#!/usr/bin/python
#
# Try Python RPC Interpreter
# Licensed under GNU GPL Version 3 license
# Copyright (c) 2011 Jakub Jankiewicz <http://jcubic.pl>
#

import os, re, sys, types
import json
from StringIO import StringIO


def uniq_id():
    try:
        from hashlib import md5
    except ImportError:
        import md5 as _md5
        md5 = _md5.new
    from time import time
    return md5(str(time())).hexdigest()


class Interpreter(object):
    def start(self):
        session_id = uniq_id()
        open('../session_%s.py' % session_id, 'w')
        return session_id

    def info(self):
        import sys
        msg = 'Type "help", "copyright", "credits" or "license" for more information.'
        return "Python %s on %s\n%s" % (sys.version, sys.platform, msg)

    def evaluate(self, session_id, code):
        global modules
        try:
            session_file = '../session_%s.py' % session_id
            fake_stdout = StringIO()
            __stdout = sys.stdout
            if code.strip() == "license":
                return "Type license() to see the full license text"
            # these in python do the same as a function but they are not show up
            # in scripts
            if re.match("^(copyright|credits)$", code.strip()):
                code = code + "()"
            env = {}
            sys.stdout = fake_stdout
            exec(open(session_file), env)
            #don's show output from privous session
            fake_stdout.seek(0)
            fake_stdout.truncate()
            ret = eval(code, env)
            result = fake_stdout.getvalue()
            sys.stdout = __stdout
            return result
        except:
            try:
                exec(code, env)
            except:
                sys.stdout = __stdout
                import traceback
                buff = StringIO()
                traceback.print_exc(file=buff)
                #don't show rpc stack
                stack = buff.getvalue().replace('"<string>"', '"<JSON-RPC>"').split('\n')
                return '\n'.join([stack[0]] + stack[3:])
            else:
                sys.stdout = __stdout
                open(session_file, 'a+').write('\n%s' % code)
                return fake_stdout.getvalue()

    def destroy(self, session_id):
        os.remove('../session_%s.py' % session_id)

def error(message):
    print "Content-Type: application/json"
    print
    print json.serialize({"error": message})

if __name__ == '__main__':
    from cgi import parse_qs
    query = parse_qs(os.environ['QUERY_STRING'])
    if not query.has_key('token'):
        error("You need to provide valid token")
    else:
        token = query['token'][0]
        if open('../config.json').read().find(token) != -1:
            json.handle_cgi(Interpreter())
        else:
            error("You need to provide valid token")

