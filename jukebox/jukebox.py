import logging, time, nfc, mpd

class Jukebox:
    def __init__(self, hostname="localhost", port="6600", timeout=10):
        self.init_nfc_client()
        self.init_music_client(hostname, port, timeout)

    def init_nfc_client(self):
        self.nfc_client = nfc.ContactlessFrontend('usb')
        self.nfc_character = None
        self.nfc_event()

    def init_music_client(self, hostname, port, timeout):
        self.music_client = mpd.MPDClient()
        self.music_client.timeout = timeout
        self.music_client.idletimeout = None
        self.music_client_hostname = hostname
        self.music_client_port = port

    def nfc_event(self):
        self.nfc_last_change = time.time()

    def connect(self):
        self.music_client.connect(self.music_client_hostname, self.music_client_port)

    def disconnect(self):
        self.music_client.close()
        self.music_client.disconnect()

    def start(self):
        self.nfc_client.connect(
            rdwr = {
                'on-connect': self.tag_connect,
                'on-release': self.tag_release,
                'beep-on-connect': True
            }
        )

    def tag_connect(self, tag):
        self.nfc_event()
        print "Connect"
        print str(tag)
        return True

    def tag_release(self, tag):
        self.nfc_event()
        print "Release"
        return False
