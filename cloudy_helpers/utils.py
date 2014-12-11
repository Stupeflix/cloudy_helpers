from cloudyclient.api import run
import os


def sync_statics(statics):
    for name, folder in statics['app_path']:
        # Add trailing /
        name = name + '/' if not name.endswith('/') else name
        folder = folder + '/' if not folder.endswith('/') else folder

        run(
            'rsync',
            '-raz',
            '-t',
            folder,
            '%s@%s:%s' % (
                statics['user'],
                statics['server'],
                os.path.join(statics['dir'], name)))
