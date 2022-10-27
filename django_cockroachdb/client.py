import os.path
import signal
import subprocess
from urllib.parse import urlencode

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
        sslmode = settings_dict['OPTIONS'].get('sslmode')
        options = settings_dict['OPTIONS'].get('options')

        url_params = {}
        insecure = True  # Default to insecure.
        # Assume all certs are in the directory that has the sslrootcert.
        if sslrootcert:
            args += ["--certs-dir=%s" % os.path.dirname(sslrootcert)]
            insecure = False
        if sslmode:
            url_params["sslmode"] = sslmode
            insecure = (sslmode == "disable")
        if options:
            url_params["options"] = options
        if insecure:
            args += ["--insecure"]
        args.extend(parameters)

        environ = os.environ.copy()
        query = urlencode(url_params)
        environ['COCKROACH_URL'] = f'postgresql://{user}:{password}@{host}:{port}/{db}?{query}'
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
