import datetime
from dropbox import client
from blog.models import Post


class DropboxInterface(object):
    date_format = '%a, %d %b %Y %H:%M:%S +%f'
    def __init__(self):
        super(DropboxInterface, self).__init__()
        self.client = client.DropboxClient(oauth2_access_token='5IeYd3-2_5wAAAAAAAAANx5NciEsxBJRY_ctKltjEJS5OVYYJCCeQL77GsFptS_I')

    def _remove_non_existant_pk(self, c):
        splt = c['path'].split('.')
        new_path = '.'.join(splt[0:-2] + [splt[-1]])
        self.mv(from_path=c['path'], to_path=new_path)
        c['path'] = new_path
        c['name'] = new_path.split('/')[-1]

    def resolve(self):
        contents = self.ls()
        for c in contents:
            pk = c.get('pk')
            if pk:
                try:
                    post = Post.objects.get(pk=pk)
                    c['post'] = post
                    latest = post.revision == c['revision']
                    if not latest and post.revision is not None:
                        c['status'] = 'Changes'
                    elif post.revision:
                        c['status'] = 'Published'
                    else:
                        c['status'] = 'Not Published'
                except Post.DoesNotExist:
                    self._remove_non_existant_pk(c)
                    c['status'] = 'Unprocessed'
                    del c['pk']
            else:
                c['status'] = 'Unprocessed'
        return contents

    def ls(self):
        """raw data from dropbox"""
        resp = self.client.metadata('')
        contents = []
        if 'contents' in resp:
            for f in resp['contents']:
                path = f['path']
                if '.md' in path:
                    # raw_modified_date = f['modified']
                    # modified_date = datetime.datetime.strptime(raw_modified_date +'00', self.date_format)
                    name = path.split('/')[-1]
                    meta = {
                        'path': path,
                        'revision': f['revision'],
                        'size': f['size'],
                        'name': name
                    }
                    try:
                        pk = int(name.split('.')[-2])
                        meta['pk'] = pk
                    except (IndexError, ValueError):
                        pass
                    contents.append(meta)
        return contents

    def processed(self):
        descriptors = self.ls()
        return [d for d in descriptors if 'pk' in descriptors]

    def unprocessed(self):
        descriptors = self.ls()
        return [d for d in descriptors if not 'pk' in descriptors]

    def read(self, path):
        f, metadata = self.client.get_file_and_metadata(path)
        return f.read(), metadata

    def mv(self, from_path, to_path):
        self.client.file_move(from_path, to_path)

    def find(self, string):
        results = self.client.search('/', string)
        return [x['path'] for x in results]

# x = DropboxInterface().ls()
# print(x)
# print(DropboxInterface().read(x[0]['path']))

print(DropboxInterface().unprocessed())