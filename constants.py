"""
A class for storing all the constants.
"""


class Constants:
    def __init__(self):
        self.OSU_MAIN_URL 	 = 'https://osu.ppy.sh'
        self.OSU_IMAGE_URL 	 = 'https://a.ppy.sh'
        self.OSU_USER_URL 	 = self.OSU_MAIN_URL + '/u/'
        self.OSU_BEATMAP_URL = self.OSU_MAIN_URL + '/b/'
        self.OSU_MATCH_URL 	 = self.OSU_MAIN_URL + '/community/matches/'

        self.PREFIX = 'f!'

        self.DATABASE = 'osu.db'
