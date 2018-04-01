import sys, logging, time, nfc, mpd, yaml, threading

from token import Token
from player import Player

class Jukebox:
    def __init__(self, token_definition_path, hostname, port, timeout):
        self.current_token = None
        self.last_token_event = None
        self.logger = self.get_logger()

        self.nfc_client = self.get_nfc_client()
        self.tokens = self.get_tokens(token_definition_path)
        self.player = self.get_player(hostname, port, timeout)
        self.lock = threading.Lock()

    def __delete__(self, instance):
        del self.player
        del self.nfc_client

    def get_logger(self):
        logger = logging.getLogger("hudlow.jukebox")
        logger.setLevel(logging.DEBUG)
        logger.addHandler(logging.StreamHandler(sys.stdout))

        return logger

    def get_nfc_client(self):
        self.create_token_event("initialize", None)

        return nfc.ContactlessFrontend('usb')

    def get_tokens(self, token_definition_path):
        with open(token_definition_path, 'r') as file:
            definitions = yaml.load(file)

            return Token.from_definitions(definitions)

    def get_player(self, hostname, port, timeout):
        return Player(self.logger, hostname, port, timeout)

    def create_token_event(self, type, token):
        name = token.name if token != None else "None"
        self.last_token_event = (type, name, time.time())

        return self.last_token_event

    def start(self):
        self.nfc_client.connect(
            rdwr = {
                'on-connect': self.tag_connect,
                'on-release': self.tag_release,
                'beep-on-connect': True
            }
        )

    def queue_music_for(self, token):
        self.logger.info("Starting music for " + token.name)

        self.player.queue_playlists(token.playlists)

    def stop_music(self):
        self.logger.info("Stopping music")

        self.player.stop_music()

    def tag_connect(self, tag):
        with self.lock:
            token = Token.find_token(tag)
            event = self.create_token_event("connect", token)

            if (token != self.current_token):
                self.current_token = token

                if (token != None):
                    self.queue_music_for(token)
                else:
                    self.stop_music()

            return True

    def tag_release(self, tag):
        with self.lock:
            token = Token.find_token(tag)
            event = self.create_token_event("release", token)

            thread = threading.Thread(target=self.check_if_token_gone, args=(event,))
            thread.start()

            return False

    def check_if_token_gone(self, event):
        time.sleep(3)

        with self.lock:
            if (self.last_token_event == event):
                self.current_token = None
                self.stop_music()
