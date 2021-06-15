from threading import Thread
import os, cv2, datetime

class SaveVideoOutput(object):
    def __init__(self, file_video_stream):
        # file_video_stream instance
        self.fvs = file_video_stream
        self.frame_width = int(self.fvs.stream.get(3))
        self.frame_height = int(self.fvs.stream.get(4))

        # name of the source
        self.source = file_video_stream.source

        # get ROOT application
        self.ROOT_DIR = os.path.abspath(os.curdir)
        print("[INFO] ROOT_DIR: " + self.ROOT_DIR)

        # Set up codec and output video settings
        self.codec = cv2.VideoWriter_fourcc('M','J','P','G')
        self.output_video = cv2.VideoWriter(self.ROOT_DIR + "/videos/" + self.source.split('/')[-1] + "_init.avi", self.codec, 30, (self.frame_width,self.frame_height))

        self.stopped = False
        self.show = False

        # inicializa variável do frame
        self.frame = 0

        # intialize thread
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True

    def start(self):
        # start a thread to read frames from the file video stream
        self.thread.start()
        return self

    def update(self):
        # Read the next frame from the stream in a different thread

        while self.fvs.more() and self.stopped == 'False':
            dtn = datetime.datetime.now()
            minute = int(dtn.strftime('%M'))
            print("[INFO] Minute: " + str(minute) + " of " + str(dtn.strftime('%Y-%m-%d_%H_%M')))

            self.frame = self.fvs.read()

            if self.show == 'True':
                cv2.imshow(self.source, self.frame)

            if (minute % 10 == 0) and (last_minute != minute):
                last_minute = minute
                self.output_video.release()
                self.output_video = cv2.VideoWriter(self.ROOT_DIR +
                    "/videos/" + self.source.split('/')[-1] + "_" + dtn.strftime('%Y-%m-%d_%H_%M') + ".avi", self.codec,
                    30, (self.frame_width, self.frame_height))

            self.output_video.write(self.frame)

        self.output_video.release()

    def show_frame(self, bool):
        # Display frames in main program
        self.show = bool

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True
        # wait until stream resources are released (producer thread might be still grabbing frame)
        self.thread.join()

