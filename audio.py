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
    is_paused = False
    just_started = False # HACK: mplayer delays slightly. Wait for it to actually load the file.
    send_lock = None
    running = True
    volume = 5
    prefix = ''
    current_pos = 0
    on_queue = True
    
    def __init__(self, prefix, save = None):
        threading.Thread.__init__(self, name="mplayer")
        self.daemon = True
        self.prefix = prefix
        self.save = save
        self.load_queue()
        self.start()
    
    def __del__(self):
        self.shutdown()
    
    def run(self):
        """This whole function is now a massive hack. Fuck mplayer."""
        devnull = open('/dev/null','w')
        self.send_lock = threading.Lock()
        self.player = Popen(["mplayer", "-input", "nodefault-bindings", "-noconfig", "all", "-slave", "-quiet", "-idle"], stdin=PIPE, stdout=PIPE, stderr=devnull)
        buff = ''
        # HACK: So we don't hang the first time.
        self.communicate("pausing_keep_force get_property path")
        while self.running:
            line = self.player.stdout.readline().strip()
            try:
                key, value = line.split('=', 1)
            except:
                continue
            # HACK
            if self.just_started:
                if key == 'ANS_path':
                    # HACK HACK HACK
                    self.communicate("pausing_keep_force get_property path")
                    if value == '(null)':
                        continue
            self.just_started = False
            if key == 'ANS_path':        
                # This is useful to check if we're playing anything, and if so, what that might be.
                # It also always returns a line of some form, so readline won't hang.
                self.communicate("pausing_keep_force get_property path")
                if value == '(null)':
                    self.on_stopped()
                else:
                    new_file = value[len(self.prefix)+1:]
                    if self.current_file != new_file:
                        self.on_changed_file(new_file)
            else:
                continue
            
            time.sleep(0.5)
    
    def on_changed_file(self, new_file):
        self.current_file = new_file
        self.set_volume(self.volume)
        try:
            self.on_queue = True
            self.current_index = self.play_queue.index(new_file)
        except ValueError:
            self.on_queue = False
    
    def on_stopped(self):
        self.current_file = None
        if self.is_playing and len(self.play_queue) > 0:
            self.skip()
        else:
            self.is_playing = False
    
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
            self.on_queue = True
            filename = self.play_queue[self.current_index]
        else:
            self.on_queue = False
        self.just_started = True
        self.is_playing = True
        self.is_paused = False
        self.communicate("loadfile \"%s/%s\"" % (self.prefix, filename))
    
    def pause(self):
        if self.current_file is not None:
            self.is_paused = not self.is_paused
            self.communicate("pause")
    
    def stop(self):
        self.is_playing = False
        self.is_paused = False
        self.communicate("stop")
        self.current_file = None
    
    def reset(self):
        if self.current_file is not None:
            self.is_paused = False
            self.communicate("seek 0 2")
    
    def skip(self, to=None):
        if to is None:
            if len(self.play_queue) > 0:
                self.current_index = (self.current_index + 1) % len(self.play_queue)
                self.play()
            return True
        else:
            if to < len(self.play_queue):
                self.current_index = to
                self.play()
                return True
            else:
                return False
    
    def back(self):
        if len(self.play_queue) > 0:
            self.current_index -= 1
            if self.current_index < 0:
                self.current_index = len(self.play_queue) - 1
            self.play()
    
    def clear_queue(self):
        self.play_queue = []
        self.save_queue()
    
    def append_to_queue(self, filename):
        if os.path.isfile('%s/%s' % (self.prefix, filename)):
            self.play_queue.append(filename)
            self.save_queue()
            return True
        else:
            return False
    
    def remove_from_queue(self, index):
        if index < len(self.play_queue):
            del self.play_queue[index]
            self.save_queue()
            if index <= self.current_index and index > 0:
                index -= 1
    
    def set_volume(self, volume):
        if volume < 0:
            volume = 0
        if volume > 10:
            volume = 10
        print "Changing volume from %s to %s." % (self.volume, volume)
        self.volume = volume
        mplayer_volume = volume * 8 # Scale from 0 - 80 (mplayer goes to 100 but sounds crap)
        self.communicate("pausing_keep_force volume %s 1" % mplayer_volume)
    
    def save_queue(self):
        if self.save is None:
            return
        try:
            f = open(self.save, 'w')
            f.write('\n'.join(self.play_queue))
            f.close()
        except IOError:
            pass
    
    def load_queue(self):
        if self.save is None:
            return
        try:
            f = open(self.save, 'r')
            self.play_queue = [x for x in f.read().split('\n') if x != '']
            f.close()
        except:
            pass
