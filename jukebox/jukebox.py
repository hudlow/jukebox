import logging, time, nfc, mpd, yaml, threading, md5
from token import Token

class Jukebox:
    def __init__(self, token_definition_path="config/tokens.yaml", hostname="localhost", port="6600", timeout=10):
        self.init_nfc_client()
        self.init_tokens(token_definition_path)
        self.init_music_client(hostname, port, timeout)
        self.current_token = None
        self.lock = threading.Lock()

    def init_nfc_client(self):
        self.nfc_client = nfc.ContactlessFrontend('usb')
        self.token_event("Initialize", "None")

    def init_tokens(self, token_definition_path):
        stream = open(token_definition_path, 'r')
        definitions = yaml.load(stream)
        self.tokens = Token.from_definitions(definitions)

    def init_music_client(self, hostname, port, timeout):
        self.music_client = mpd.MPDClient()
        self.music_client.timeout = timeout
        self.music_client.idletimeout = None
        self.music_client_hostname = hostname
        self.music_client_port = port

    def token_event(self, type, name):
        self.last_token_event = (type, name, time.time())
        return self.last_token_event

    def connect(self):
        self.music_client.connect(self.music_client_hostname, self.music_client_port)

    def disconnect(self):
        self.music_client.close()
        self.music_client.disconnect()

    def start(self):
        self.connect()
        self.nfc_client.connect(
            rdwr = {
                'on-connect': self.tag_connect,
                'on-release': self.tag_release,
                'beep-on-connect': True
            }
        )

    def tag_connect(self, tag):
        self.lock.acquire()

        token = Token.find_token(tag)
        name = token.name if token != None else "None"
        event = self.token_event("connect", name)

        if (token == self.current_token):
            self.lock.release()
            return True

        self.current_token = token

        if (token != None):
            print "Start music for " + token.name

        self.lock.release()
        return True

    def tag_release(self, tag):
        self.lock.acquire()

        token = Token.find_token(tag)
        name = token.name if token != None else "None"
        event = self.token_event("connect", name)

        thread = threading.Thread(target=self.check_if_token_gone, args=(event,))
        thread.start()

        self.lock.release()
        return False

    def check_if_token_gone(self, event):
        time.sleep(3)
        self.lock.acquire()

        if (self.last_token_event != event):
            self.lock.release()
            return False

        print "Stop music for " + self.current_token.name
        self.current_token = None

        self.lock.release()
        return True
