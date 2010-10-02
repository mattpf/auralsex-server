from subprocess import Popen, PIPE, STDOUT
import threading
import time

class AudioPlayer(threading.Thread):
    player = None
    current_file = None
    is_paused = False
    
    def __init__(self):
        threading.Thread.__init__(self, name="mplayer")
        self.daemon = True
        self.start()
    
    def __del__(self):
        self.shutdown()
    
    def shutdown(self):
        if self.player is not None:
            self.communicate("quit")
    
    def run(self):
        devnull = open('/dev/null','w')
        self.player = Popen(["mplayer", "-input", "nodefault-bindings", "-noconfig", "all", "-slave", "-quiet", "-idle"], stdin=PIPE, stdout=PIPE, stderr=devnull)
        buff = ''
        sleep = True
        while True:
            # This is useful to check if we're playing anything, and if so, what that might be.
            # It also always returns a line of some form, so readline won't hang.
            
            self.communicate("pausing_keep_force get_property path")
        
            buff = self.player.stdout.readline().strip()
            parts = buff.split('\n')
            for line in parts:
                try:
                    key, value = line.split('=', 1)
                except:
                    sleep = False
                    continue
                else:
                    if key == '':
                        sleep = False
                    else:
                        sleep = True
                if key == 'ANS_path':
                    if value == '(null)':
                        self.current_file = None
                    else:
                        self.current_file = value
            
            if sleep:
                time.sleep(1)
            
    
    def communicate(self, message):
        """Send a message to the mplayer backend (with error handling)"""
        try:
            self.player.stdin.write("%s\n" % message)
        except IOError:
            self.current_file = None
    
    def play(self, filename):
        """Plays the given filename, stopping anything currently playing"""
        if self.current_file is not None:
            self.stop()
    
        self.communicate("loadfile \"%s\"" % filename)
        self.current_file = filename
    
    def pause(self):
        if self.current_file is not None:
            self.communicate("pause\n")
    
    def stop(self):
        if self.current_file is not None:
            self.communicate("stop\n")
            self.current_file = None
    
    def reset(self):
        if self.current_file is not None:
            self.communicate("seek 0 2\n")
