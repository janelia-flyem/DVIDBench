import json
import sys
import requests
import tempfile
import os
import re
import time
import shlex
from tabulate import tabulate
from pkg_resources import resource_filename
from subprocess import call, Popen, PIPE

# http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
def which(program):
    import os
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def stderr_info(path, row):
    with open(path) as log:
        for line in log:
            trans_match = re.match(r'Transaction rate:\s+([\d\.]*)', line)
            longest_match = re.match(r'Longest transaction:\s+([\d\.]*)', line)
            shortest_match = re.match(r'Shortest transaction:\s+([\d\.]*)', line)
            if trans_match:
               trans_match.group(1)
            if longest_match:
                row[2] = longest_match.group(1)
            if shortest_match:
                row[1] = shortest_match.group(1)

def stdout_info(path):
    log = open(path, 'r')
    return log.read()






class Benchmark:

    def __init__(self, args):
        self.load_settings(args)
        return

    def run (self):

        return

    def load_settings (self, args):
        if args.get('debug'):
            sys.stderr.write("looking for settings in %s\n" % args['config'])

        try:
            config_json = open(args['config'])
            config = json.load(config_json)
        except IOError:
            raise ConfigError(msg = "unable to find the config file: %s\n" % args['config'])
        except ValueError:
            raise ConfigError(msg = "There was a problem reading the config. Is it valid JSON?\n")

        # merge the command line args with the ones loaded from the config file.
        # command line always wins.
        config.update(args)

        self.config = config
        return


    def get_repo_info (self):
        if not self.config.get('host'):
            raise ConfigError(msg='The supplied configuration json is missing the "host" key/value pair')

        server_info_url = "http://%s/api/repos/info" % self.config.get('host')
        try:
            response = requests.get(server_info_url)
        except requests.exceptions.ConnectionError:
            raise RemoteError(msg='There was a problem contacting the server at %s. Is it available?' % self.config.get('host', 'unknown'))

        if response.status_code != 200:
            raise RemoteError(msg='There was a problem contacting the server at {0}. Got a {1} response'.format(self.config.get('host', 'unknown'), response.status_codea))

        return response.json()

    def check_siege_installed(self):
        siege_path = ''
        if 'siege_path' in self.config:
            siege_path = which(self.config.get('siege_path'))
        else:
            print "searching for siege application..."
            siege_path = which('siege')

        if not siege_path:
            sys.stderr.write('siege does not appear to be installed in your PATH. Please install it or add the full path to your configuration\n')
            sys.exit(1)

        if self.config.get('debug'):
            print "using siege found at %s" % siege_path

        self.config['siege_path'] = siege_path
        return

    def create_temporary_urls_file (self):
        if not self.config.get('urls'):
            raise ConfigError( msg = 'The "urls" key/value pair is missing from your configuration file.')

        #open temporary file for writing
        urls = tempfile.NamedTemporaryFile()
        for url in self.config.get('urls'):
            urls.write(url + "\n")

        urls.flush()
        return urls

    def verify_or_create_log_dir(self):
        if not self.config.get('logs'):
            raise ConfigError( msg = 'The "logs" key/value pair is missing from your configuration file. This should be a path to a directory where the results will be saved')
        if not os.path.isdir(self.config['logs']):
            os.makedirs(self.config['logs'])
        return

    def create_log_file(self):
        if 'results' in self.config and self.config['results']:
            self.config['log_prefix'] = self.config.get('results')
        else:
            self.config['log_prefix'] = time.strftime("%Y%m%d-%H%M%S-") + str(os.getpid())

        self.config['log_file'] = os.path.join(self.config['logs'], self.config['log_prefix'] + '.log')

        return self.config.get('log_file')

    def min_connections(self):
        min = self.config.get('min_connections',0)
        # start the range at 0 otherwise we get 1, 21, 41, 61 instead of 1, 20, 40, 60
        if min <= 1 and self.config.get('increments', 50) > 1:
            min = 0
        return min

    def max_connections(self):
        max = self.config.get('max_connections',500) + 1
        return max

    def display_results(self):

        log_file = self.config.get('log_file')

        if not os.path.exists(log_file):
            sys.stderr.write("Couldn't find results for {}.\n".format(self.config.get('log_prefix')))
            sys.exit(1)

        print "Displaying results for test {}.".format(self.config.get('log_prefix'))

        tabular_data = []
        headers = ["Concurrent Requests", "Fastest", "Slowest", "Avg", "Failures"]

        # open the log file and dump it to the terminal
        with open(log_file) as summary:
            row_data = [None] * 5
            for line in summary:
                con_match = re.match(r'\*{4} (\d+)', line)
                sum_match = re.match(r'\d{4}-\d{2}-\d{2}', line)
                if con_match:
                    connections = con_match.group(1)
                    row_data[0] = connections

                    stderr_log_path = os.path.join(self.config['logs'], self.config['log_prefix']) + '-' + str(connections) + '-stderr.log'
                    if self.config.get('debug'):
                        print "checking {}".format(stderr_log_path)
                    stderr_info(stderr_log_path, row_data)

                    if self.config.get('debug'):
                        print "looking at logs {0}".format(stderr_log_path)
                elif sum_match:
                    sum_data = [ x.strip() for x in line.split(',')]
                    row_data[3] = sum_data[4]
                    row_data[4] = sum_data[9]
                    tabular_data.append(row_data)
                    row_data = [None] * 5

        print tabulate(tabular_data, headers=headers, tablefmt="fancy_grid")
        return

    def execute_siege(self, concurrent):


        siege_config = resource_filename(__name__, 'siege.dat')
        cmd = '{program} -R{config} -d1 -t{duration}s -c{concurrent} -f{urls} -l{log} -m{message}'.format(
            program    = self.config['siege_path'],
            config     = siege_config,
            duration   = self.config.get('duration', 5),
            concurrent = concurrent,
            urls       = self.urls_file.name,
            log        = self.config.get('log_file'),
            message    = concurrent
        )
        if self.config.get('debug'):
            print cmd
        args = shlex.split(cmd)
        proc = Popen(args, stdout=PIPE, stderr=PIPE)
        out, err = proc.communicate()
        exitcode = proc.returncode
        if self.config.get('debug'):
            print out # displays individual url timings
            print err # displays runtime summaries

        # save the results to disk / sqlite database?
        stdout_log = open(os.path.join(self.config['logs'], self.config['log_prefix']) + '-' + str(concurrent) + '-stdout.log' ,'a')
        stdout_log.write(out)

        stderr_log = open(os.path.join(self.config['logs'], self.config['log_prefix']) + '-' + str(concurrent) + '-stderr.log' ,'a')
        stderr_log.write(err)

        return

    def prepare_run(self):

        if self.config.get('results'):
            self.create_log_file()

        else:
            # contact the configured server and make sure it is alive
            repo_info = self.get_repo_info()

            # print out repo list and ask which one to use if one isn't specified in settings
            #if not 'repo' in config:
            #    config['repo'] = repo_selection(repo_info)

            self.check_siege_installed()

            self.urls_file = self.create_temporary_urls_file()

            self.verify_or_create_log_dir()

            self.create_log_file()


            # go through the users in incremental steps from min to max as configured by
            # the user.

        return self.config.get('log_file')

    def run(self):

        if not self.config.get('results'):
            for i in range(self.min_connections(), self.max_connections(), self.config.get('increments', 50)):
                # always have at least one connection.
                concurrent = i
                if concurrent < 1:
                    concurrent = 1
                print "checking {0} concurrent connections".format(concurrent)
                self.execute_siege(concurrent)
                time.sleep(5)

        # parse the results and provide a summary output.
        self.display_results()
        return


#######################################
# Error Classes

class Error(Exception):
    pass

class ConfigError(Exception):

    def __init__(self, msg):
        self.msg = msg

class RemoteError(Exception):

    def __init__(self, msg):
        self.msg = msg
