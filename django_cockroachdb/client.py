import os.path
import subprocess

from django.db.backends.base.client import BaseDatabaseClient


class DatabaseClient(BaseDatabaseClient):
    executable_name = 'cockroach'

    @classmethod
    def settings_to_cmd_args(cls, settings_dict):
        args = [cls.executable_name, 'sql']
        db = settings_dict['OPTIONS'].get('db', settings_dict['NAME'])
        user = settings_dict['OPTIONS'].get('user', settings_dict['USER'])
        passwd = settings_dict['OPTIONS'].get('passwd', settings_dict['PASSWORD'])
        host = settings_dict['OPTIONS'].get('host', settings_dict['HOST'])
        port = settings_dict['OPTIONS'].get('port', settings_dict['PORT'])
        server_ca = settings_dict['OPTIONS'].get('ssl', {}).get('ca')

        if db:
            args += ["--database=%s" % db]
        # The cockroach command needs the directory in which all the certs are
        # stored in. Use the directory where the server_ca is located in as the
        # base directoery for the command.
        if server_ca:
            args += ["--certs-dir=%s" % os.path.dirname(server_ca)]
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
        return args

    def runshell(self):
        args = DatabaseClient.settings_to_cmd_args(self.connection.settings_dict)
        subprocess.check_call(args)
