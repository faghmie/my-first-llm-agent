import sys
import time
import threading
from itertools import cycle

class BusyAnimation:
    def __init__(self, delay=0.5):
        self.delay = delay
        self.frames = ["∙∙∙∙∙", "●∙∙∙∙", "●●∙∙∙", "●●●∙∙", "●●●●∙", "●●●●●"]
        
        # self.frames = ["\033[36m⠋\033[0m", "\033[34m⠙\033[0m", "\033[35m⠹\033[0m", 
        #  "\033[33m⠸\033[0m", "\033[32m⠼\033[0m", "\033[31m⠴\033[0m"]

        # self.frames = [
        #     "\033[36m●∙∙∙∙∙\033[0m",  # Cyan
        #     "\033[34m∙●∙∙∙∙\033[0m",  # Blue
        #     "\033[35m∙∙●∙∙∙\033[0m",  # Magenta
        #     "\033[33m∙∙∙●∙∙\033[0m",  # Yellow
        #     "\033[32m∙∙∙∙●∙\033[0m",  # Green
        #     "\033[31m∙∙∙∙∙●\033[0m",  # Red
        #     "\033[32m∙∙∙∙●∙\033[0m",  # Green
        #     "\033[33m∙∙∙●∙∙\033[0m",  # Yellow
        #     "\033[35m∙∙●∙∙∙\033[0m",  # Magenta
        #     "\033[34m∙●∙∙∙∙\033[0m"   # Blue
        # ]
        self.running = False
        self.thread = None
        self.start_time = None  

    def animate(self):
        for frame in cycle(self.frames):
            if not self.running:
                break

            # Calculate elapsed time
            elapsed = time.time() - self.start_time
            mins, secs = divmod(int(elapsed), 60)
            timer_str = f"\033[90m[{mins:02}:{secs:02}]\033[0m"  # Grey color
            
            # Combine frame with timer
            sys.stdout.write(f"\r{frame}  {timer_str}")
            sys.stdout.flush()
            time.sleep(self.delay)

    def __enter__(self):
        # Hide cursor
        sys.stdout.write("\x1b[?25l")
        sys.stdout.flush()
        self.running = True
        self.start_time = time.time()
        self.thread = threading.Thread(target=self.animate)
        self.thread.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.running = False
        self.thread.join()
        # Clear animation and restore cursor
        sys.stdout.write("\r\033[K")
        sys.stdout.write("\x1b[?25h")
        sys.stdout.flush()

if __name__ == "__main__":

    def get_response():
        # Simulate long-running task
        time.sleep(5)
        return "Here's the answer to your question..."

    print("Processing your request...")
    with BusyAnimation():
        result = get_response()
    
    print("\nResponse received:")
    print(result)