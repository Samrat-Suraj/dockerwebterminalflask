## import module

from gevent.socket import wait_read, wait_write
import fcntl
import gevent
import os
import pty
import binascii
import setproctitle
import signal
import struct
import subprocess
import sys
import termios

import pyte

class TerminalManager(object):
    def __init__(self,ws=None):
        self.terminals = {}
        self.ws = ws

    def __getitem__(self, _id):
        return self.terminals[_id]

    def __contains__(self, _id):
        return _id in self.terminals

    def list(self):
        return [{
            'id': _id,
            'command': self[_id].command,
        } for _id in self.terminals.keys()]

    def create(self, **kwargs):
        _id = binascii.hexlify(os.urandom(32)).decode('utf-8')
        t = Terminal(self,id=_id,ws=self.ws,**kwargs)
        self.terminals[_id] = t
        return _id

    def kill(self, _id):
        self.terminals[_id].kill()
        self.remove(_id)

    def remove(self, _id):
        self.terminals.pop(_id)


class Terminal():
    def __init__(self,manager=None, id=None, ws=None, command=None,autoclose=False, log=None,autoclose_retain=5):
        self.width = 80
        self.height = 25
        self.id = id
        self.manager = manager
        self.autoclose = autoclose
        self.autoclose_retain = autoclose_retain
        self.ws = ws
        self.log = log
        env = {}
        env.update(os.environ)
        env['TERM'] = 'linux'
        env['COLUMNS'] = str(self.width)
        env['LINES'] = str(self.height)
        env['LC_ALL'] = 'en_US.UTF8'

        self.command = command
        if not self.command:
            shell = os.environ.get('SHELL', None)
            if not shell:
                for sh in ['zsh', 'bash', 'sh']:
                    try:
                        shell = subprocess.check_output(['which', sh])
                        break
                    except Exception as e:
                        pass
            self.command = shell

        args = ['sh', '-c', self.command]
        exe = 'sh'

        self.log.info('Activating new terminal: %s', self.command)

        self.pid, self.fd = pty.fork()
        if self.pid == 0:
            setproctitle.setproctitle('%s terminal session #%i' % (sys.argv[0], os.getpid()))
            os.execvpe(exe, args, env)

        self.log.info('Subprocess PID %s', self.pid)

        self.dead = False

        fl = fcntl.fcntl(self.fd, fcntl.F_GETFL)
        fcntl.fcntl(self.fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

        self.stream_in = os.fdopen(self.fd, 'rb', 0)
        self.stream_out = os.fdopen(self.fd, 'wb', 0)
        self.pyte_stream = pyte.Stream()
        self.screen = pyte.DiffScreen(self.width, self.height)
        self.pyte_stream.attach(self.screen)

        self.last_cursor_position = None

        self.reader = gevent.spawn(self.reader_fn)

    def reader_fn(self):
        while True:
            wait_read(self.fd)
            self.run_single_read()
            self._check()
            if self.dead:
                return

    def run_single_read(self):
        try:
            data = self.stream_in.read()
        except IOError:
            data = ''

        if data:
            try:
                self.pyte_stream.feed(data.decode('utf-8'))
                self.ws.send(data)
            except UnicodeDecodeError:
                pass

    def _check(self):
        try:
            pid, status = os.waitpid(self.pid, os.WNOHANG)
        except OSError:
            self.on_died(code=0)
            return
        if pid:
            self.on_died(code=status)

    def on_died(self, code=0):
        if self.dead:
            return

        self.log.info('Terminal %s has died', self.id)
        self.dead = True

        if code:
            self.pyte_stream.feed(u'\n\n * ' + u'Process has exited with status %i' % code)
        else:
            self.pyte_stream.feed(u'\n\n * ' + u'Process has exited successfully')


        if self.autoclose:
            gevent.spawn_later(self.autoclose_retain, self.manager.remove, self.id)

        """
        TODO
        if self.callback:
            try:
                self.callback(exitcode=code)
            except TypeError:
                self.callback()
        """

    def has_updates(self):
        if self.last_cursor_position != (self.screen.cursor.x, self.screen.cursor.y):
            return True
        return len(self.screen.dirty) > 0

    def feed(self, data):
        wait_write(self.fd)
        self.stream_out.write(data.encode('utf-8'))
        self.stream_out.flush()

    def resize(self, w, h):
        if self.dead:
            return
        if (h, w) == (self.screen.lines, self.screen.columns):
            return
        if w <= 0 or h <= 0:
            return
        self.width = w
        self.height = h
        self.log.info('Resizing terminal to %sx%s', w, h)
        self.screen.resize(h, w)
        winsize = struct.pack("HHHH", h, w, 0, 0)
        fcntl.ioctl(self.fd, termios.TIOCSWINSZ, winsize)

    def kill(self):
        self.reader.kill(block=False)

        self.log.info('Killing subprocess PID %s', self.pid)
        try:
            os.killpg(self.pid, signal.SIGTERM)
        except OSError:
            pass
        try:
            os.kill(self.pid, signal.SIGKILL)
        except OSError:
            pass
