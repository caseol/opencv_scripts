from threading import Thread
import cv2


class SaveVideoOutput(object):
    def __init__(self, source, output):
        # name of the source
        self.source = source
        # Set up codec and output video settings
        self.output_video = output

        # inicializa variável do frame
        self.frame = 0

        # Start the thread to read frames from the video stream
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()

    def update(self):
        # Read the next frame from the stream in a different thread
        while True:
            True

    def show_frame(self, frame):
        # Display frames in main program
        if frame is not None:
            self.frame = frame
            cv2.imshow(self.source, self.frame)

    def save_frame(self, frame):
        # Save obtained frame into video output file
        self.output_video.write(frame)