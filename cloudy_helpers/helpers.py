import os.path as op

from cloudy_helpers.utils import sync_statics
from cloudyclient.api import PythonDeployScript, render_template, sudo, run, cd


class GruntUwsgiDeployScript(PythonDeployScript):
    '''
    Deployment with nginx + grunt + uwsgi.
    '''

    use_wheel = True
    conf_files = []
    requirements = []

    # statics = {
    #     'server': '',
    #     'dir': '',
    #     'user': '',
    #     'app_path': [
    #         ('app', 'relative_path'),
    #     ]
    # }

    def setup_packages(self):
        pass

    def copy_conf_files(self):
        # Copy configuration files
        for src, dst_path in self.conf_files:
            src = op.join('deploy', src)
            dst_parts = dst_path.split('.')
            dst = self.dvars
            while dst_parts:
                part = dst_parts.pop(0)
                try:
                    dst = dst[part]
                except KeyError:
                    raise ValueError(
                        'deployment variable not found "%s"' %
                        dst_path)
            dst_dir = op.dirname(dst)
            if not op.isdir(dst_dir):
                sudo('mkdir', dst_dir)
            context = self.get_config_context()
            render_template(
                src,
                dst,
                context=context,
                use_jinja=True,
                use_sudo=True)

    def npm_install(self):
        npm_dir = op.expanduser(self.dvars['npm_dir'])

        run('cp', '-f', 'package.json', op.join(npm_dir, '..', 'package.json'))
        with cd(op.join(npm_dir, '..')):
            run('npm', 'install', '-d')

        run('ln', '-sf', npm_dir, 'node_modules')

    def deploy_with_grunt(self):
        self.npm_install()
        run('bower', 'install')
        run('grunt', 'build')

    def install(self):
        self.copy_conf_files()
        self.deploy_with_grunt()

        # Sync statics to a custom server
        if hasattr(self, 'statics'):
            sync_statics(self.statics)

    def get_config_context(self, **kwargs):
        context = self.dvars.copy()
        context.update(kwargs)
        context['base_dir'] = self.ddata['base_dir']
        context['dist_dir'] = op.abspath(op.join(
            op.dirname(__file__), '..', 'dist'))
        context['static_dir'] = op.join(context['dist_dir'], 'static')
        return context

    def restart_backend_process(self):
        sudo('supervisorctl', 'update')
        # Gracefuly restart web backend
        sudo('touch', self.dvars['uwsgi']['touch_reload'])

    def post_install(self):
        self.restart_backend_process()
        # Create nginx symlink and reload
        nginx_conf_file = self.dvars['nginx']['conf_file']
        nginx_conf_basename = op.basename(nginx_conf_file)
        nginx_conf_symlink = op.join(
            '/etc/nginx/sites-enabled',
            nginx_conf_basename)
        sudo('ln', '-sfn', nginx_conf_file, nginx_conf_symlink)
        sudo('/etc/init.d/nginx', 'reload')
