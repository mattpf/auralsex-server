import audio
import webserver

player = None

def handle_play(request):
    if 'filename' in request.query:
        player.play(request.query['filename'][0])
    else:
        player.play()
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

def handle_add(request):
    if 'filename' not in request.query:
        request.output('missing filename', response_code=400)
        return
    if player.append_to_queue(request.query['filename'][0]):
        request.output('ok')
    else:
        request.output('music not found', response_code=404)

def handle_clear(request):
    player.clear_queue()
    request.output("ok")

def handle_remove(request):
    if 'filename' not in request.query:
        request.output('missing filename', response_code=400)
        return
    filename = request.query['filename'][0]
    if filename in player.play_queue:
        player.remove_from_queue(filename)
        request.output("ok")
    else:
        request.output("already missing", response_code=410)

def handle_skip(request):
    player.skip()
    request.output("ok")
    
def handle_back(request):
    player.back()
    request.output("ok")

def bind(new_player):
    global player
    player = new_player
    webserver.set_get_handler("/play", handle_play)
    webserver.set_get_handler("/pause", handle_pause)
    webserver.set_get_handler("/stop", handle_stop)
    webserver.set_get_handler("/reset", handle_reset)
    webserver.set_get_handler("/add", handle_add)
    webserver.set_get_handler("/clear", handle_clear)
    webserver.set_get_handler("/remove", handle_remove)
    webserver.set_get_handler("/skip", handle_skip)
    webserver.set_get_handler("/back", handle_back)
