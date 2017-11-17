import traceback
import uuid
import paramiko
import reco_config

def sftp_upload(fname, image):

    client = paramiko.SSHClient()

    res = False

    try:
       
        client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy)

        client.connect(
            hostname=reco_config.sftp_host, 
            username=reco_config.sftp_username, 
            password=reco_config.sftp_password)

        sftp = client.open_sftp()

        fr = sftp.file(fname, 'wb')
        fr.set_pipelined(True)

        try:
            fr.write(image)
        finally:
            fr.close()

        res = True

    except:

        #traceback.print_exc()
        print("sending to sftp failed...")

    finally:

        if client:
            client.close()
       
    return res

def test():
    
    fname = reco_config.sftp_path + str(uuid.uuid4()) + '.jpg'
    print ("fname", fname)
    
    sftp_upload(fname, b'1234455678')

if __name__ == '__main__':
    test()
