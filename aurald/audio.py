from subprocess import Popen, PIPE, STDOUT
import threading
import time
import os

class AudioPlayer(threading.Thread):
    player = None
    current_file = None
    
    play_queue = []
    current_index = 0
    looping = True
    is_playing = False
    just_started = False # HACK: mplayer delays slightly. Wait for it to actually load the file.
    send_lock = None
    running = True
    
    def __init__(self):
        threading.Thread.__init__(self, name="mplayer")
        self.daemon = True
        self.start()
    
    def __del__(self):
        self.shutdown()
    
    def run(self):
        """This whole function is now a massive hack. Fuck mplayer."""
        devnull = open('/dev/null','w')
        self.send_lock = threading.Lock()
        self.player = Popen(["mplayer", "-input", "nodefault-bindings", "-noconfig", "all", "-slave", "-quiet", "-idle"], stdin=PIPE, stdout=PIPE, stderr=devnull)
        buff = ''
        sleep = True
        # HACK: So we don't hang the first time.
        self.communicate("pausing_keep_force get_property path")
        while self.running:
            line = self.player.stdout.readline().strip()
            if self.just_started:
                self.just_started = False
                time.sleep(3)
                if line[0:8] == 'ANS_path':
                    self.communicate("pausing_keep_force get_property path")
                continue
            try:
                key, value = line.split('=', 1)
            except:
                sleep = False
                continue
            
            if key == 'ANS_path':        
                # This is useful to check if we're playing anything, and if so, what that might be.
                # It also always returns a line of some form, so readline won't hang.
                
                self.communicate("pausing_keep_force get_property path")
                if value == '(null)':
                    self.current_file = None
                    if self.is_playing and len(self.play_queue) > 0:
                        self.current_index = (self.current_index + 1) % len(self.play_queue)
                        self.play(self.play_queue[self.current_index])
                else:
                    if self.current_file != value:
                        self.current_file = value
                        try:
                            self.current_index = self.play_queue.index(value)
                        except IndexError:
                            self.current_index = -1
            else:
                continue
            
            time.sleep(1.0)
    
    def shutdown(self):
        self.running = False
        if self.player is not None:
            self.communicate("quit")
    
    def communicate(self, message):
        """Send a message to the mplayer backend (with error handling)"""
        try:
            with self.send_lock:
                self.player.stdin.write("%s\n" % message)
        except IOError:
            self.current_file = None
    
    def play(self, filename=None):
        """
        If a filename is given, plays the given filename, stopping anything currently playing.
        If none is given, plays whatever is in the queue
        """
        if self.current_file is not None:
            self.stop()
        
        if filename is None:
            if len(self.play_queue) == 0:
                return False
            filename = self.play_queue[self.current_index]
        self.current_file = filename
        self.just_started = True
        self.is_playing = True
        self.communicate("loadfile \"%s\"" % filename)
    
    def pause(self):
        if self.current_file is not None:
            self.communicate("pause")
    
    def stop(self):
        is_playing = False
        self.communicate("stop")
        self.current_file = None
    
    def reset(self):
        if self.current_file is not None:
            self.communicate("seek 0 2")
    
    def clear_queue(self):
        self.play_queue = []
    
    def append_to_queue(self, filename):
        if os.path.isfile(filename):
            self.play_queue.append(filename)
            return True
        else:
            return False
    
    def remove_from_queue(self, filename):
        if filename in self.play_queue:
            self.play_queue.remove(filename)
