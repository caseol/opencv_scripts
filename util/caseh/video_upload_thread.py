from threading import Thread
import os
import sys
import datetime
import shutil
import pysftp

class VideoUploadThread(object):
    def __init__(self):

        # flag control
        self.stopped = False
        self.dt = datetime.datetime.now()

        self.host = "api.orbis.net.br"
        self.pem_file = '~/.ssh/authorized_keys/orbisicar.pem'

        # Start the thread to read frames from the video stream
        self.thread = Thread(target=self.upload_video, args=())
        self.thread.daemon = True

    def start(self):
        # start a thread to read frames from the file video stream
        self.thread.start()
        return self

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True
        self.thread.join()

    def upload_video(self):
        while True:
            # if the thread indicator variable is set, stop the
            # thread
            if self.stopped:
                break

            #  percorre a pasta e faz o upload de cada arquivo e depois move
            for filename in os.listdir('videos/'):
                try:
                    if filename.endswith(".avi"):
                        with pysftp.Connection(self.host, username='ubuntu', private_key=self.pem_file) as sftp:
                            _target = '/home/ubuntu/railsapp/orbis_proxy/public/videos/' + filename
                            _video_path = 'videos/' + filename
                            sftp.put(_video_path, _target)
                            shutil.move(_video_path, 'videos/uploaded/')

                except Exception:
                    print("[UPLOADER] Deu merda! " + str(sys.exc_info()))