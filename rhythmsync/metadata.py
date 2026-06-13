from mutagen import File
from re import match

import rhythmsync.terminal_disp as terminal_disp


# tag map
def get_tag_map():
    return {
        "title": ["title", "TIT2", "TITLE", "©nam"],
        "artist": ["artist", "TPE1", "ARTIST", "©ART"],
        "album": ["album", "TALB", "ALBUM", "©alb"],
        "albumartist": ["albumartist", "TPE2", "ALBUMARTIST", "aART"],
        "date": ["date", "TDRC", "YEAR", "©day"],
        "copyright": ["copyright", "TCOP", "copyright"],
        "publisher": ["publisher", "TPUB"],
        "tracknumber": ["tracknumber", "TRCK"],
        "discnumber": ["discnumber", "TPOS"],
        "description": ["description", "COMM", "desc"],
        "lyrics": ["SYLT", "SYLT::eng", "LYRICS", "LYRICS:eng", "LYRICS-ENG", "LYRICS_EN", "LYRICS_SYNCED", "SYNCEDLYRICS", "USLT", "USLT::eng"],
        "genre": ["genre", "TCON", "©gen"]
    }


# get meatadata for info command
def get_metadata(file_path, tags=None):
    try:
        audio = File(file_path)
        if audio is None or audio.tags is None:
            terminal_disp.error_msg(f"Unsupported or unreadable file: {file_path}", "Metadata")
            return None
        tag_map = get_tag_map()
        reverse_map = {}
        for canonical, variants in tag_map.items():
            for variant in variants:
                reverse_map[variant.lower()] = canonical

        normalized_tags = None
        if tags is not None:
            normalized_tags = {tag.lower() for tag in tags}

        lines = []

        for key, value in audio.tags.items():
            canonical = reverse_map.get(key.lower(), key.lower())

            if normalized_tags is not None:
                if canonical.lower() not in normalized_tags:
                    continue

            if hasattr(value, "text"):
                value = value.text

            if isinstance(value, (list, tuple)):
                value = "; ".join(str(v) for v in value)
            else:
                value = str(value)

            lines.append(
                f"[green]{canonical}[/green]: {value}"
            )

        return "\n".join(lines)

    except Exception as e:
        terminal_disp.error_msg(e, "Metadata")
        return None


# get title and artist info for the player
def get_ti_ar(file_path):
    try:
        audio = File(file_path)
        if audio is None or audio.tags is None:
            return f"Unknown Title", "Unknown Artist"
        tag_map = get_tag_map()
        reverse_map = {}
        for canonical, keys in tag_map.items():
            for k in keys:
                reverse_map[k.lower()] = canonical

        title = None
        artist = None

        for key, value in audio.tags.items():
            canonical = reverse_map.get(key.lower())

            if canonical == "title" and title is None:
                if hasattr(value, "text"):
                    value = value.text

                if isinstance(value, (list, tuple)):
                    title = str(value[0])
                else:
                    title = str(value)

            elif canonical == "artist" and artist is None:
                if hasattr(value, "text"):
                    value = value.text

                if isinstance(value, (list, tuple)):
                    artist = str(value[0])
                else:
                    artist = str(value)

        if not title:
            title = f"Unknown Title"

        if not artist:
            artist = "Unknown Artist"

        return title, artist
    
    except Exception as e:
        return f"Unknown Title", "Unknown Artist"


# get and format lyrics from the audio file for the player
def get_lrc(file_path):
    try:
        audio = File(file_path)

        if audio is None or audio.tags is None:
            return None

        lrc_tag_names = ['SYLT', 'SYLT::eng', 'LYRICS', 'LYRICS:eng', 'LYRICS-ENG', 'LYRICS_EN', 'LYRICS_SYNCED', 'SYNCEDLYRICS']

        # fetch lyrics
        for tag in lrc_tag_names:
            if tag in audio.tags:

                value = audio.tags[tag]

                if tag.startswith("SYLT"):
                    try:
                        return "\n".join([t[2] for t in value[0].text])
                    except Exception:
                        raw_lyrics = value[0]
                    
                raw_lyrics = value[0] if isinstance(value, list) else value

                # format lyrics
                timestamp = r"^\[\d{2}:\d{2}\.\d{2}\]"

                lrc_lines = raw_lyrics.split("\n")
            
                lyrics = [[line[1:9],line[10:].strip()] for line in lrc_lines if match(timestamp, line)]
            
                lyrics.insert(0,['00:00.00', ""])
            
                for x in lyrics:
                    if x[1] == "":
                        x[1] = "♫"

                return lyrics

        return None

    except Exception as e:
        return None


# get meatadata for the info panel (player)
def get_info(file_path):
    try:
        info = {
            "title": "Unknown Title",
            "artist": "Unknown Artist",
            "album": "Unknown Album",
            "genre": "Unknown Genre",
            "date": "Unknown Date",
            "sample_rate": "Unknown Sample Rate"
        }
                
        audio = File(file_path)
        
        if audio is None or audio.tags is None:
            return info
        
        tag_map = get_tag_map()
        reverse_map = {}

        for canonical, variants in tag_map.items():
            for variant in variants:
                reverse_map[variant.lower()] = canonical

        tags = ["title", "artist", "album", "genre", "date"]

        for key, value in audio.tags.items():
            canonical = reverse_map.get(key.lower(), key.lower())

            if canonical not in tags:
                continue

            if hasattr(value, "text"):
                value = value.text

            if isinstance(value, (list, tuple)):
                value = "; ".join(str(v) for v in value)
            else:
                value = str(value)

            info[canonical] = value
        
        info["sample_rate"] = f"{audio.info.sample_rate/1000:.2f} kHz"

        return info

    except Exception as e:
        return {
            "title": "Unknown Title",
            "artist": "Unknown Artist",
            "album": "Unknown Album",
            "genre": "Unknown Genre",
            "date": "Unknown Date",
            "sample_rate": "Unknown Sample Rate"
        }