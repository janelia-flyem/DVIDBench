import sys
import os

class Configurable():
    def __init__(self, options):
        pass

    def load_config_data(self, args):
        if args.debug:
            sys.stderr.write("looking for settings in %s\n" % args.config_file)

        self.config_file = args.config_file

        expanded = os.path.expanduser(self.config_file)
        if os.path.exists(expanded):
            if self.config_file.endswith('.py'):
                abs_path = os.path.abspath(expanded)
                directory, configfile = os.path.split(abs_path)
                # change the python path
                sys.path.insert(0, directory)
                # import file as a python object
                imported = __import__(os.path.splitext(configfile)[0])
                config = imported.DVIDConfig()
                import ipdb; ipdb.set_trace()
                return config

        # couldn't open the config file
        print "unable to open the configuration file: {}".format(expanded)
        exit(0)
