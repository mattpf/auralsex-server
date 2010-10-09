#!/usr/bin/env python
import webserver
import audio
import webglue
import sys

def main():
    player = audio.AudioPlayer(sys.argv[1])
    webglue.bind(player)
    try:
        print "AuralSex ready."
        webserver.serve()
    except KeyboardInterrupt:
        player.shutdown()
        print "Goodbye."

if __name__ == '__main__':
    main()