import sys
from watchdog.events import FileSystemEvent, PatternMatchingEventHandler
from watchdog.observers import Observer
import time

  
class Handler(PatternMatchingEventHandler):
    files = []

    def __init__(self):
        # Set the patterns for PatternMatchingEventHandler
        PatternMatchingEventHandler.__init__(
            self, patterns=['*.txt', '*.py'], ignore_patterns=['.*'], ignore_directories=True)
  
    def on_created(self, event):
        # Event is created, you can process it now
        if event.src_path not in self.files:
            self.files.append(event.src_path) 

  
    def on_modified(self, event):
        # Event is modified, you can process it now
        if event.src_path not in self.files:
            self.files.append(event.src_path) 
  
  
if __name__ == "__main__":
    src_path = sys.argv[1] if len(sys.argv) > 1 else '.'
    event_handler = Handler()
    observer = Observer()
    observer.schedule(event_handler, src_path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(5)
            if event_handler.files:
                for f in event_handler.files:
                    print(f)
                    event_handler.files.remove(f)
            else:
                continue
    except KeyboardInterrupt:
        observer.stop()
        observer.join()