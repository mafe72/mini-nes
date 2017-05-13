#!/usr/bin/env python2.7

import traceback
import argparse
import signal
import grp
import daemon
from daemon import pidfile
import nfc_poll

debug_p = True

def start_daemon( pidf, logf ):
    # This launches the daemon in its context

    global debug_p

    if debug_p:
        print( "nfc_poll_daemon: entered start_daemon()")
        print( "nfc_poll_daemon: pidf={}  logf={}".format( pidf, logf ) )

    try:
        with daemon.DaemonContext(
            working_directory='/var/lib/nfc_poll',
            gid = grp.getgrnam( 'nes' ).gr_gid,
            umask=0o002,
            pidfile=pidfile.TimeoutPIDLockFile( pidf ),
            ) as context:

            logger = nfc_poll.initLogger( logf )
            logger.debug( "nfc_poll_daemon: entered daemon context" )

            try:
                options = nfc_poll.initConfig()
                logger.debug( "nfc_poll_daemon: options: {}".format( options ) )

                app = nfc_poll.NFCPoll( options, logger )
                context.signal_map = {
                    signal.SIGTERM: app.cleanup
                    }
                logger.debug( "nfc_poll_daemon: running app" )
                app.run()
            except:
                logger.error( tracebox.format_exc() )
                sys.exit(1)

    except:
        print( "Unhandled Exception: {}".format( traceback.format_exc() ) )
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser( description="NFC Poll Daemon" )
    parser.add_argument( '-p', '--pid-file', default='/var/run/nfc_poll.pid' )
    parser.add_argument( '-l', '--log-file', default='/var/log/nfc_poll.log' )

    args = parser.parse_args()

    start_daemon( args.pid_file, args.log_file )
