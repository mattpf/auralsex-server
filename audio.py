import audiere

import webserver

class AudioPlayer:
    player = None
    current_file = None
    volume = 1.0

    def __init__(self):
        self.player = audiere.open_device()

    def play(self, filename):
        """Plays the given filename, stopping anything currently playing"""
        if self.current_file is not None:
            self.stop()
        
        self.current_file = self.player.open_file(filename, True)
        self.current_file.volume = 1.0
        self.current_file.play()
        print self.current_file
    
    def pause(self):
        if self.current_file is not None:
            self.current_file.pause()
    
    def stop(self):
        if self.current_file is not None:
            del self.current_file
    
    def reset(self):
        if self.current_file is not None:
            self.current_file.reset()
    

