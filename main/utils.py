import requests

from online_school_site.settings import YOUTUBE_API_TOKEN

YOUTUBE_API_LINK = 'https://www.googleapis.com/youtube/v3/videos?part=snippet%2CcontentDetails%2Cstatistics'


def get_video_title(video_id):
    response = requests.get('%s&id=%s&key=%s' % (YOUTUBE_API_LINK, video_id, YOUTUBE_API_TOKEN))
    if 200 <= response.status_code <= 299:
        print(response.json())
        return response.json()['items'][0]['snippet']['title']

    return ''


def get_video_id(link):
    if 'embed' in link:
        return link.split('/embed/')[-1]

    return link.split('watch?v=')[-1]
