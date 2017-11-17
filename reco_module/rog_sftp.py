import traceback
import uuid
import paramiko
import reco_config

def sftp_upload(fname, image):
    
    res = False

    try:

        with paramiko.SSHClient() as client:

            client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy)

            client.connect(
                hostname=reco_config.sftp_host, 
                username=reco_config.sftp_username, 
                password=reco_config.sftp_password)

            with client.open_sftp() as sftp: 
                with sftp.file(fname, 'wb') as fr:
                    fr.set_pipelined(True)
                    fr.write(image)
                    res = True

    except:

        #traceback.print_exc()
        print("sending to sftp failed...")

    return res

def test():
    
    fname = reco_config.sftp_path + str(uuid.uuid4()) + '.jpg'
    print ("fname", fname)
    
    sftp_upload(fname, b'1234455678')

if __name__ == '__main__':
    test()
