import re

class Token:
    name_lookup = {}
    identifier_lookup = {}

    def __init__(self, name, identifiers, playlists):
        self.name = name
        self.identifiers = identifiers
        self.playlists = playlists

        Token.name_lookup[name] = self

        for identifier in self.identifiers:
            Token.identifier_lookup[identifier] = self

    @staticmethod
    def from_definition(definition):
        identifiers = set(definition["identifiers"])
        playlists = []

        for playlist_definition in definition["playlists"]:
            playlists.append((playlist_definition["name"], playlist_definition["mode"]))

        return Token(definition["name"], identifiers, playlists)

    @staticmethod
    def from_definitions(definitions):
        tokens = set()

        for definition in definitions:
            tokens.add(Token.from_definition(definition))

        return tokens

    @staticmethod
    def find_token(tag):
        result = re.findall('ID=([0-9A-Za-z]+)', str(tag))

        if len(result) == 0:
            return None

        identifier = result[0]

        if identifier in Token.identifier_lookup:
            return Token.identifier_lookup[identifier]
        else:
            return None
