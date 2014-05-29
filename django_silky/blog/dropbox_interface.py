from dropbox import client

class DropboxInterface(object):
    def __init__(self):
        super(DropboxInterface, self).__init__()
        self.client = client.DropboxClient(oauth2_access_token='5IeYd3-2_5wAAAAAAAAANx5NciEsxBJRY_ctKltjEJS5OVYYJCCeQL77GsFptS_I')

    def ls(self):
        resp = self.client.metadata('')
        contents = []
        if 'contents' in resp:
            for f in resp['contents']:
                if '.md' in f['path']:
                    contents.append({
                        'path': f['path'],
                        'revision': f['revision'],
                        'modified': f['modified'],
                        'size': f['size']
                    })
        return contents

    def read(self, path):
        f, metadata = self.client.get_file_and_metadata(path)
        return f.read()



x = DropboxInterface().ls()
print(DropboxInterface().read(x[0]['path']))