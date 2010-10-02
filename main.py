#!/usr/bin/env python
import webserver
import audio
import webglue

def main():
    player = audio.AudioPlayer()
    webglue.bind(player)
    webserver.serve()

if __name__ == '__main__':
    main()