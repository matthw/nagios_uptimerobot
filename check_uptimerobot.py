#!/usr/bin/python
# v1.0 Matthieu Walter 2017
#

import sys
import json
import getopt
from urllib import urlencode
from urllib2 import Request, urlopen

API_KEY = "insert-api-key"


STATUS = (
    'PAUSED',           #0
    'NOT_CHECKED_YET',  #1
    'UP',               #2
    'NO_USED',          #3
    'NO_USED',          #4
    'NO_USED',          #5
    'NO_USED',          #6
    'NO_USED',          #7
    'SEEMS_DOWN',       #8
    'DOWN'
)

# NAGIOS exit codes
NAG_UNKNOWN = 3
NAG_CRITICAL = 2
NAG_WARNING = 1
NAG_OK = 0


def error(msg):
    sys.stderr.write(msg + '\n')
    sys.stderr.flush()
    sys.exit(NAG_UNKNOWN)


class UptimeRobot:
    api_url = 'https://api.uptimerobot.com/v2/'

    def __init__(self, api_key):
        self.api_key = api_key

    def post(self, method, params={}, headers={}):
        url = UptimeRobot.api_url + method
        params['api_key'] = API_KEY
        params['format'] = 'json'
        req = Request(url, urlencode(params), headers)
        try:
            return json.loads(urlopen(req).read())
        except Exception, e:
            error("Failed: "+str(e))
            return []

    def getMonitors(self, name=None):
        ''' returns all monitors or just the specified one
        '''
        mons = self.post('getMonitors')
        if not mons.has_key('monitors'):
            error('Failed: cannot get monitors')

        # all monitors
        if name is None:
            return mons['monitors']

        # specific one
        name = name.lower()
        for m in mons['monitors']:
            if m['friendly_name'].lower() == name:
                return m

        return None


    def listMonitors(self):
        ''' returns a list of monitors names
        '''
        mons = self.getMonitors()
        return [m['friendly_name'] for m in mons]


    def getStatus(self, name):
        monitor = self.getMonitors(name)
        if not monitor:
            error("Failed: cannot get monitor '%s'"%name)

        return {'name': name,
                'print_status': STATUS[monitor['status']],
                'status': monitor['status'],
                'url': monitor['url']
               }

def usage():
    print "usage %s [-hl] [monitor]"%sys.argv[0]
    print ""
    print "    -h      --help      This help"
    print "    -l      --list      List available monitors"
    

def main(argv):
    try:
        opts, args = getopt.getopt(argv[1:], "hl", ["help", "list"])
    except getopt.GetoptError as err:
        print str(err)
        usage()
        sys.exit(NAG_UNKNOWN)

    ur = UptimeRobot(API_KEY)

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-l", "--list"):
            print "Available monitors:"
            for m in ur.listMonitors():
                print "* '%s'"%m

            sys.exit(NAG_UNKNOWN)

    if not len(args):
        error("Error: missing argument")
    if len(args) > 1:
        error("Error: too many arguments")

    data = ur.getStatus(args[0])
    if not data:
        error("Cannot get monitor")

    else:
        print "%s (%s) is %s"%(data['name'], data['url'], data['print_status'])
        # nagios status
        if data['status'] in (0, 1):
            sys.exit(NAG_WARNING)
        elif data['status'] in (7, 8):
            sys.exit(NAG_CRITICAL)
        elif data['status'] == 2:
            sys.exit(NAG_OK)
        else:
            sys.exit(NAG_UNKNOWN)
            
    


if __name__ == "__main__":
    main(sys.argv)

    # by default return unknown
    exit(NAG_UNKNOWN)
