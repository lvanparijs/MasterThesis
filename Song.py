class Song:

    def __init__(self, file_name, analyse):
        if file_name is None:
            print("NO FILENAME GIVEN")
        else:
            self.file_name = file_name  # Path to the music file