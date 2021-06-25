from threading import Thread
import cv2, time, datetime


class SaveVideoOutput(object):
    def __init__(self, source, queue, fps=12):
        # flag control
        self.stopped = False
        self.Q = queue
        self.fps = fps

        # name of the source
        self.video_source = source

        self.dt = datetime.datetime.now()

        # Set up codec and output video settings
        self.codec = cv2.VideoWriter_fourcc('M','J','P','G')
        self.output_path = "videos/" + self.video_source.split('/')[-1] + "_" + self.dt.strftime('%Y-%m-%d_%H_%M') + ".avi"
        self.output_video = cv2.VideoWriter(self.output_path, self.codec, self.fps, (640, 480))

        # inicializa variável do frame
        self.frame = 0

        # Start the thread to read frames from the video stream
        self.thread = Thread(target=self.save_frame, args=())
        self.thread.daemon = True

    def start(self):
        # start a thread to read frames from the file video stream
        self.thread.start()
        return self

    def save_frame(self):
        # Read the next frame from the stream in a different thread
        last_minute = -1
        while True:
            # if the thread indicator variable is set, stop the
            # thread
            if self.stopped:
                break

            # otherwise, ensure the queue has room in it
            if not self.Q.full():
                self.frame = self.Q.get()

                dtn = datetime.datetime.now()
                minute = int(dtn.strftime('%M'))

                if (minute % 10 == 0) and (last_minute != minute):
                    last_minute = minute
                    self.output_video.release()
                    self.output_path = "videos/" + self.video_source.split('/')[-1] + "_" + dtn.strftime('%Y-%m-%d_%H_%M') + ".avi"
                    self.output_video = cv2.VideoWriter(self.output_path, self.codec, self.fps, (640, 480))
                    print("[INFO] " + self.output_path + " criado!")

                self.output_video.write(self.frame)
                print("[INFO] frame saved! " + self.output_path)
            else:
                print("[INFO] fila cheia! dando tempo para o worker trabalhar..." + self.output_path)
                time.sleep(0.1)  # Rest for 10ms, we have a full queue

        print("[INFO] Fim da gravação" + self.output_path)

    def show_frame(self):
        # Display frames in main program
        cv2.imshow(self.video_source, self.frame)

        # Press Q on keyboard to stop recording
        key = cv2.waitKey(1)
        if key == ord('q'):
            self.output_video.release()
            cv2.destroyAllWindows()
            exit(1)

    def more(self):
        # return True if there are still frames in the queue. If stream is not stopped, try to wait a moment
        tries = 0
        while self.Q.qsize() == 0 and not self.stopped and tries < 10:
            time.sleep(0.2)
            tries += 1

        return self.Q.qsize() > 0