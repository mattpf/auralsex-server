import audio
import webserver

player = None

def handle_play(request):
    print "Playing '%s'" % request.query['filename'][0]
    player.play(request.query['filename'][0])
    request.output("ok")

def handle_pause(request):
    player.pause()
    request.output("ok")

def handle_stop(request):
    player.stop()
    request.output("ok")

def handle_reset(request):
    player.reset()
    request.output("ok")

def bind(new_player):
    global player
    player = new_player
    webserver.set_get_handler("/play", handle_play)
    webserver.set_get_handler("/pause", handle_pause)
    webserver.set_get_handler("/stop", handle_stop)
    webserver.set_get_handler("/reset", handle_reset)