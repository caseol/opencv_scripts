from pathlib import Path
from threading import Thread
import cv2, time, datetime

class VideoStreamWidget(object):
    def __init__(self, src='/dev/video0'):
        self.src = src
        self.capture = cv2.VideoCapture(src)
        # define o codec para a criação do vídeo
        vid_cod = cv2.VideoWriter_fourcc(*'XVID')
        # define o output do arquivo com 20 FPS e dimensão 640x480
        self.output = cv2.VideoWriter("videos/" + src.split('/')[-1] + "_init.avi", vid_cod, 20.0, (640, 480))

        # Start the thread to read frames from the video stream
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()

    def update(self):
        # Read the next frame from the stream in a different thread
        while True:
            if (self.capture.isOpened()):
                (self.status, self.frame) = self.capture.read()
                if (self.status):
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    # dt = str(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
                    dt = str(datetime.datetime.now())
                    frame = cv2.putText(self.frame, dt, (348, 20), font, 0.7, (0, 0, 0), 2, cv2.INTER_LINEAR_EXACT)
                    self.output.write(self.frame)

            time.sleep(.01)

    def show_frame(self):
        # Display frames in main program
        cv2.imshow(str(self.src), self.frame)
        key = cv2.waitKey(1)
        if key == ord('q'):
            self.capture.release()
            cv2.destroyAllWindows()
            exit(1)

    def get_file_size(file):
        size = Path(file).stat().st_size
        return size

if __name__ == '__main__':
    video_stream_widget0 = VideoStreamWidget('/dev/video0')
    video_stream_widget2 = VideoStreamWidget('/dev/video2')
    while True:
        try:
            video_stream_widget0.show_frame()
            video_stream_widget2.show_frame()
        except AttributeError:
            pass