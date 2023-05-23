import os
import subprocess
import re

def get_twitch_channel_name():
    while True:
        twitch_link = input("Please enter the Twitch channel link or name: ")
        if 'twitch.tv/' in twitch_link:
            channel_name = twitch_link.split('twitch.tv/')[1]
            return channel_name
        elif re.match(r'^[\w-]+$', twitch_link):
            return twitch_link
        else:
            print("The link format is incorrect. Please re-enter.")

def get_stream_quality_options(channel_name):
    command = f"streamlink twitch.tv/{channel_name}"
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()

    if process.returncode != 0:
        print("The channel is currently offline, or re-check your link.")
        return None
    else:
        quality_options = re.findall(r"(\d+p\d*|audio_only)", output.decode('utf-8'))
        # sort based on resolution, higher to lower and audio_only at the end
        quality_options = sorted(list(set(quality_options)), key=lambda x: -int(re.search(r'\d+', x).group()) if x != 'audio_only' else float('inf'))
        return quality_options

def select_stream_quality(quality_options):
    print("Available quality options:")
    for i, option in enumerate(quality_options, start=1):
        print(f"[{i}] {option}")

    while True:
        choice = input("Please select a quality option by number: ")
        if choice.isdigit() and 1 <= int(choice) <= len(quality_options):
            return quality_options[int(choice) - 1]
        else:
            print("Invalid choice. Please select a valid number.")

def get_stream_url(channel_name, quality):
    command = f"streamlink --stream-url twitch.tv/{channel_name} {quality}"
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, error = process.communicate()

    if process.returncode != 0:
        print("Error getting stream URL.")
        return None
    else:
        return output.decode('utf-8').strip()

def record_stream(stream_url):
    output_file_base = "twitchLive"
    output_file_ext = ".mp4"
    n = 0
    while True:
        output_file = f"{output_file_base}{n if n > 0 else ''}{output_file_ext}"
        if not os.path.exists(output_file):
            break
        n += 1
    command = f"ffmpeg -i {stream_url} -c copy {output_file}"
    process = subprocess.Popen(command, shell=True)
    process.wait()

    if process.returncode != 0:
        print("There was an error during the recording.")
    else:
        print(f"Recording saved as {output_file}")

def main():
    channel_name = get_twitch_channel_name()
    quality_options = get_stream_quality_options(channel_name)
    if quality_options:
        selected_quality = select_stream_quality(quality_options)
        stream_url = get_stream_url(channel_name, selected_quality)
        if stream_url:
            record_stream(stream_url)

if __name__ == "__main__":
    main()
