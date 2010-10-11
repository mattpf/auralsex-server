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
    try:
        player.skip(int(request.query['to'][0]) if 'to' in request.query else None)
        request.output("ok")
    except TypeError:
        request.output("to what, exactly?", response_code=400)
    
def handle_back(request):
    player.back()
    request.output("ok")

def list_tracks(request):
    request.output("\n".join(player.play_queue))

def current_index(request):
    request.output(str(player.current_index))

def current_file(request):
    request.output(player.current_file)

def current_volume(request):
    request.output(str(player.volume))

def handle_volume(request):
    if 'volume' in request.query:
        try:
            volume = int(request.query['volume'][0])
        except:
            request.output("bad volume", response_code=400)
            return
        player.set_volume(volume)
    request.output(str(player.volume))

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
    webserver.set_get_handler("/list", list_tracks)
    webserver.set_get_handler("/current", current_index)
    webserver.set_get_handler("/current_file", current_file)
    webserver.set_get_handler("/volume", handle_volume)
