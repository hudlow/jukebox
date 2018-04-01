import mpd, socket, math, time

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
        assume_connected = True

        while (attempt < 5):
            if attempt > 2:
                seconds = math.pow(2, attempt-2)
                self.logger.warning("Waiting for " + str(seconds) + " seconds...")
                time.sleep(seconds)

            if not assume_connected:
                self.logger.warning("Attempting to reconnect to MPD")
                assume_connected = self.connect_music_client()

            if assume_connected:
                try:
                    return getattr(self.music_client, name)(*arguments)
                except mpd.ConnectionError:
                    pass

                assume_connected = False
                self.logger.warning("Could not send command")

            attempt += 1

        raise PlayerCommandError("Failed to send command to MPD")

    def queue_playlists(self, playlists):
        try:
            self.clear()

            count = 0
            for playlist in playlists:
                songs = self.listplaylistinfo(playlist[0])

                length = len(songs)

                self.load(playlist[0])

                if (playlist[0] == "shuffle"):
                    self.shuffle(str(count) + ":" + str(count+length))

                count += length

            self.play()

            return True
        except PlayerCommandError:
            self.logger.error("Failed to play music")
            return False

    def stop_music(self):
        try:
            self.stop()
            self.clear()

            return True
        except PlayerCommandError:
            self.logger.error("Failed to stop music")
            return False

class PlayerCommandError(Exception):
    pass
