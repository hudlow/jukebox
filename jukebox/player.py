import mpd, socket

class Player:
    def __init__(self, logger, hostname, port, timeout):
        self.logger = logger
        self.hostname = hostname
        self.port = port
        self.music_client = self.get_music_client(timeout)
        self.connect_music_client()

    def __delete__(self, instance):
        self.disconnect()

    def __getattr__(self, name):
        return lambda *arguments: self.proxy(name, *arguments)

    def get_music_client(self, timeout):
        music_client = mpd.MPDClient()
        music_client.timeout = timeout
        music_client.idletimeout = None

        return music_client

    def connect_music_client(self):
        try:
            self.music_client.connect(self.hostname, self.port)
            return True
        except socket.error:
            self.logger.error("Failed to connect to MPD")
            return False

    def disconnect(self):
        try:
            self.music_client.ping()
        except mpd.ConnectionError:
            return

        self.music_client.close()

    def proxy(self, name, *arguments):
        attempt = 1

        while (attempt < 4):
            if attempt > 1:
                seconds = math.pow(2, attempt-1)
                self.logger.warning("Waiting for " + str(seconds) + " seconds...")
                wait()

            try:
                return getattr(self.music_client, name)(*arguments)
            except mpd.ConnectionError:
                self.logger.warning("Attempting to reconnect to MPD")
                attempt += 1
                connected = self.connect_music_client()
                if not connected:
                    return False

        self.logger.error("Failed to send command to MPD")
        return False

    def queue_playlists(self, playlists):
        if self.ping() is False:
            return

        self.clear()

        count = 0
        for playlist in playlists:
            songs = self.listplaylistinfo(playlist[0])

            if not songs:
                return

            length = len(songs)

            self.load(playlist[0])

            if (playlist[0] == "shuffle"):
                self.shuffle(str(count) + ":" + str(count+length))

            count += length

        self.play()

    def stop_music(self):
        if self.ping() is False:
            return

        self.stop()
        self.clear()
