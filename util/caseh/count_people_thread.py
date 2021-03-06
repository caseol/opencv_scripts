# import the necessary packages
from queue import Queue
from threading import Thread, Lock
import cv2
from vidgear.gears import CamGear
import time, datetime


class VideoCaptureThread:
    def __init__(self, path, queue=Queue(maxsize=1024), transform=None):
        # initialize the file video stream along with the boolean
        # used to indicate if the thread should be stopped or not
        options = {
            "CAP_PROP_FRAME_WIDTH": 640,
            "CAP_PROP_FRAME_HEIGHT": 480,
            "CAP_PROP_FPS": 10,
        }
        self.stream = CamGear(source=path, logging=True, **options).start()
        # self.stream = cv2.VideoCapture(path)
        self.frame = self.stream.read()

        self.stopped = False
        self.transform = transform
        self.inverted_frame = False

        # inicializa variável do frame

        # used to record the time at which we processed current frame
        self.new_frame_time = 0
        self.prev_frame_time = 0

        # initialize the queue used to store frames read from
        # the video file
        # self.Q = Queue(maxsize=queue_size)
        self.Q = queue
        # add the frame to the queue
        if self.frame is not None:
            self.Q.put(self.frame)

        # intialize thread
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        # self.read_lock = Lock()

    def start(self):
        # start a thread to read frames from the file video stream
        self.thread.start()
        return self

    def update(self):
        frame_idx = 0
        last_sec = -1
        # keep looping infinitely
        while True:
            # if the thread indicator variable is set, stop the
            # thread
            if self.stopped:
                break

            # otherwise, ensure the queue has room in it
            if not self.Q.full():
                # read the next frame from the file
                frame = self.stream.read()
                if self.inverted_frame:
                    frame = cv2.flip(frame, -1)

                # display the image width, height, and number of channels to our
                # terminal
                # print("width: {} pixels".format(frame.shape[1]))
                # print("height: {}  pixels".format(frame.shape[0]))
                # print("channels: {}".format(frame.shape[2]))

                # Calculating the fps
                self.new_frame_time = time.time()
                # fps will be number of frame processed in given time frame
                # since their will be most of time error of 0.001 second
                # we will be subtracting it to get more accurate result
                fps = 1 / (self.new_frame_time - self.prev_frame_time)
                self.prev_frame_time = self.new_frame_time

                # converting the fps into integer
                fps = int(fps)
                # converting the fps to string so that we can display it on frame
                # by using putText function
                fps = str(fps)

                if frame is not None:
                    # if there are transforms to be done, might as well
                    # do them on producer thread before handing back to
                    # consumer thread. ie. Usually the producer is so far
                    # ahead of consumer that we have time to spare.
                    #
                    # Python is not parallel but the transform operations
                    # are usually OpenCV native so release the GIL.
                    #
                    # Really just trying to avoid spinning up additional
                    # native threads and overheads of additional
                    # producer/consumer queues since this one was generally
                    # idle grabbing frames.
                    if self.transform:
                        frame = self.transform(frame)

                    dtn = datetime.datetime.now()
                    sec = int(dtn.strftime('%S'))

                    if (last_sec != sec):
                        frame_idx = 1
                    else:
                        frame_idx = frame_idx + 1
                    last_sec = sec

                    cv2.putText(frame, "FPS: " + fps + "|Frame: " + str(frame_idx), (10, 20), cv2.FONT_HERSHEY_SIMPLEX,
                                0.5,
                                (0, 255, 0), 2)
                    # add the frame to the queue
                    self.Q.put(frame)
            else:
                time.sleep(0.1)  # Rest for 10ms, we have a full queue

        self.stream.release()

    def read(self):
        # return next frame in the queue
        return self.Q.get()

    # Insufficient to have consumer use while(more()) which does
    # not take into account if the producer has reached end of
    # file stream.
    def running(self):
        return self.more() or not self.stopped

    def more(self):
        # return True if there are still frames in the queue. If stream is not stopped, try to wait a moment
        tries = 0
        while self.Q.qsize() == 0 and not self.stopped and tries < 5:
            time.sleep(0.1)
            tries += 1

        return self.Q.qsize() > 0

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True
        # wait until stream resources are released (producer thread might be still grabbing frame)
        self.thread.join()
