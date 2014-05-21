"""
Package up silky for a release.
"""
import os
import shutil
import sys

import jinja2
import subprocess


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
DIST_DIR = SCRIPT_DIR + '/dist/{version}'


def main():
    try:
        version = sys.argv[1]
        dist_dir = DIST_DIR.format(version=version)
        if not os.path.exists(dist_dir):
            os.makedirs(dist_dir)
        with open(SCRIPT_DIR + '/setup.py.jinja2') as f:
            template = jinja2.Template(f.read())
        with open(dist_dir + '/setup.py', 'w') as f:
            f.write(template.render(version=version))
        readme_file_name = '/README.rst'
        license_file_name = '/LICENSE'
        manifest_file_name = '/MANIFEST.in'
        for file_name in readme_file_name, license_file_name, manifest_file_name:
            shutil.copyfile(SCRIPT_DIR + file_name, dist_dir + file_name)
        silky_dir = dist_dir + '/silky/'
        if os.path.exists(silky_dir):
            shutil.rmtree(silky_dir)
        shutil.copytree(SCRIPT_DIR + '/django_silky/silky/', silky_dir)
        cmd = 'cd %s && python setup.py sdist' % dist_dir
        print cmd
        subprocess.call(cmd, shell=True)
        archive_name = 'django-silky-%s.tar.gz' % version
        from_file = dist_dir + ('/dist/' + archive_name)
        to_file = dist_dir + '/../' + archive_name
        print 'Copying from %s to %s' % (from_file, to_file)
        shutil.copy2(from_file, to_file)
        shutil.rmtree(dist_dir)
    except IndexError:
        print 'Usage: %s <version>' % sys.argv[0]


if __name__ == '__main__':
    main()