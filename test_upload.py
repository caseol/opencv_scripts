import pysftp
import sys
import os

cloud_path = '/home/ubuntu/railsapp/orbis_proxy/public/videos/recon_2021-11-09_03_22.avi'
local_path = '/home/coliveira/Workspace/Python/OpenCVScripts/videos/recon_2021-11-09_03_22.avi'

host = "api.orbis.net.br"                    #hard-coded
pem_file = '~/.ssh/authorized_keys/orbisicar.pem'

for filename in os.listdir('videos/'):
    try:
        if filename.endswith(".avi"):
            with pysftp.Connection(host, username='ubuntu', private_key=pem_file) as sftp:
                _target = '/home/ubuntu/railsapp/orbis_proxy/public/videos/' + filename
                _video_path = 'videos/' + filename
                sftp.put(_video_path, _target)

    except Exception:
        print("[UPLOADER] Deu merda! " + str(sys.exc_info()))

with pysftp.Connection(host, username='ubuntu', private_key=pem_file) as sftp:
    sftp.put(local_path, cloud_path)