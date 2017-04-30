#!/usr/bin/pyton2.7

from ctypes import *
import time
import signal
import daemon
import lockfile

libnfc = CDLL("libnfc.so")
libnfcutils = CDLL("libnfcutils.so")

debug = True
interval = 5 # seconds
uiPollNr = 1 # number of times to poll each interval
uiPeriod = 1 # nfc polling periods each interval

def nfc_open():
    res = libnfcutils.nfcutils_open()

    if res < 0:
        raise OSError( "Error: Unable to open NFC device: {0}".format( res ) )
    else:
        if debug:
            print "NFC Device Open"

def nfc_close():
    res = libnfcutils.nfcutils_close()

def nfc_poll( uiPollNr, uiPeriod ):
    charArray20 = c_char * 20
    uidString = charArray20()

    res = libnfcutils.nfcutils_poll( uiPollNr, uiPeriod, uidString )

    if res < 0:
        # On my chipset, it returns a -90 Internal Chip Error when the tag is
        # not present. This sucks as it sounds like a valid error code, but
        # we have to ignore that error as it's a normal condition.
        if debug:
            print( "Warning: nfc poll: {0}".format( res ) )
        return None
    elif res == 0:
        print "No NFC tag found"
        return None
    elif res == 1:
        print "NFC tag found: {0}".format( uidString.value )
        return uidString.value

def program_setup():
    if debug:
        print "program_setup"

    nfc_open()

def program_main():
    if debug:
        print "program_main"

    while True:
        uid = nfc_poll( uiPollNr, uiPeriod )

        if uid:
            if debug:
                print "Found NFC tag: {0}".format( uid )

        time.sleep( interval )

def program_cleanup():
    if debug:
        print "program_cleanup"

    nfc_close()

def program_reload_config():
    print "Reload config"

context = daemon.DaemonContext(
        working_directory='/var/lib/nfc_poll',
        umask=0o002,
        pidfile=lockfile.FileLock( '/var/run/nfc_poll.pid' ),
    )

context.signal_map = {
        signal.SIGTERM: program_cleanup,
        signal.SIGHUP: program_reload_config,
    }

program_setup()

with context:
    program_main()

