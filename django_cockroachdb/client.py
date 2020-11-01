import os.path
import signal
import subprocess

from django.db.backends.base.client import BaseDatabaseClient


class DatabaseClient(BaseDatabaseClient):
    executable_name = 'cockroach'

    @classmethod
    def settings_to_cmd_args_env(cls, settings_dict, parameters):
        args = [cls.executable_name, 'sql']
        db = settings_dict['NAME']
        user = settings_dict['USER']
        password = settings_dict['PASSWORD']
        host = settings_dict['HOST']
        port = settings_dict['PORT']
        sslrootcert = settings_dict['OPTIONS'].get('sslrootcert')

        if db:
            args += ["--database=%s" % db]
        # Assume all certs are in the directory that has the sslrootcert.
        if sslrootcert:
            args += ["--certs-dir=%s" % os.path.dirname(sslrootcert)]
            insecure = False
        else:
            # Default to insecure if no ca exists.
            insecure = True
        if user:
            args += ["--user=%s" % user]
        if host:
            args += ["--host=%s" % host]
        if port:
            args += ["--port=%s" % port]
        if insecure:
            args += ["--insecure"]
        args.extend(parameters)
        # Use the COCKROACH_URL environment variable to securely provide the
        # password.
        environ = os.environ.copy()
        if password:
            environ['COCKROACH_URL'] = f'postgresql://{user}:{password}@{host}:{port}/{db}'
        return args, environ

    def runshell(self, parameters):
        args, environ = self.settings_to_cmd_args_env(self.connection.settings_dict, parameters)
        sigint_handler = signal.getsignal(signal.SIGINT)
        try:
            # Allow SIGINT to pass to `cockroach sql` to abort queries.
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            subprocess.run(args, check=True, env=environ)
        finally:
            # Restore the original SIGINT handler.
            signal.signal(signal.SIGINT, sigint_handler)
