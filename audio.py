from subprocess import Popen, PIPE, STDOUT

class AudioPlayer:
    player = None
    current_file = None
    volume = 1.0

    def play(self, filename):
        """Plays the given filename, stopping anything currently playing"""
        if self.current_file is not None:
            self.stop()
    
        self.current_file = Popen(["mplayer", "-input", "nodefault-bindings", "-noconfig", "all", "-slave", "-quiet", filename], stdin=PIPE)
    
    def pause(self):
        if self.current_file is not None:
            self.current_file.stdin.write("pause\n")
    
    def stop(self):
        if self.current_file is not None:
            self.current_file.communicate("stop\n")
            self.current_file = None
    
    def reset(self):
        if self.current_file is not None:
            self.current_file.stdin.write("seek 0 2\n")
