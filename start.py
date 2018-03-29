import yaml
from jukebox.jukebox import Jukebox;

def main():
    with open("config/jukebox.yaml", 'r') as file:
        config = yaml.load(file)

        box = Jukebox(config["tokens"]["definition_path"],
                      config["music_client"]["hostname"],
                      config["music_client"]["port"],
                      config["music_client"]["timeout"])
        box.start()

if __name__ == "__main__":
    main()
