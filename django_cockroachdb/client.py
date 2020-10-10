import os.path
import subprocess

from django.db.backends.base.client import BaseDatabaseClient


class DatabaseClient(BaseDatabaseClient):
    executable_name = 'cockroach'

    @classmethod
    def settings_to_cmd_args(cls, settings_dict, parameters):
        args = [cls.executable_name, 'sql']
        db = settings_dict['OPTIONS'].get('db', settings_dict['NAME'])
        user = settings_dict['OPTIONS'].get('user', settings_dict['USER'])
        passwd = settings_dict['OPTIONS'].get('passwd', settings_dict['PASSWORD'])
        host = settings_dict['OPTIONS'].get('host', settings_dict['HOST'])
        port = settings_dict['OPTIONS'].get('port', settings_dict['PORT'])
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
        if passwd:
            args += ["--password=%s" % passwd]
        if host:
            args += ["--host=%s" % host]
        if port:
            args += ["--port=%s" % port]
        if insecure:
            args += ["--insecure"]
        args.extend(parameters)
        return args

    def runshell(self, parameters):
        args = DatabaseClient.settings_to_cmd_args(self.connection.settings_dict, parameters)
        subprocess.check_call(args)
