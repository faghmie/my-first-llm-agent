import tkinter as tk
import threading
import time

class TimerWindow:
    def __init__(self):
        self.done_event = threading.Event()
        self.root = None
        self.result = None
        self.elapsed_time = None
        self.process_thread = None

    def __enter__(self):
        self.root = tk.Tk()
        self.root.title("Elapsed Time")
        self.start_time = time.time()
        self.label = tk.Label(self.root, text="0.0 seconds", font=('Helvetica', 24))
        self.label.pack(padx=20, pady=20)
        self._update_time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.root.mainloop()  # Start GUI processing after process completes
        self.done_event.set()

    def _format_time(self, seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        return f"{hours:02}:{minutes:02}:{seconds:05.2f}"

    def _update_time(self):
        elapsed = time.time() - self.start_time
        formatted_time = self._format_time(elapsed)
        
        if self.done_event.is_set():
            self.elapsed_time = formatted_time
            self.label.config(text=f"Done! {formatted_time}")
            self.root.after(2000, self.root.destroy)
            return
        
        self.label.config(text=formatted_time)
        self.root.after(100, self._update_time)

    def run_in_background(self, target):
        """Run the target function in a background thread"""
        self.process_thread = threading.Thread(target=self._wrapper, args=(target,))
        self.process_thread.start()

    def _wrapper(self, target):
        self.result = target()
        self.done_event.set()

if __name__ == "__main__":
    # Usage example
    def long_process():
        """Your long-running process"""
        time.sleep(15)  # Replace with actual work


    with TimerWindow() as timer:
        timer.run_in_background(long_process)