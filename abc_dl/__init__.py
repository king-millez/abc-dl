import argparse, sys, os, hashlib, json, re, shutil, glob, subprocess
from requests import get
from bs4 import BeautifulSoup

NEWS = 'abcnews'
TRIPLEJ = 'likeaversion'
FFMPEG = None
RADIO = 'radio'

if(sys.platform == 'win32'):
    if(shutil.which('ffmpeg.exe') is not None):
        FFMPEG = 'ffmpeg.exe'
else:
    if(shutil.which('ffmpeg') is not None):
        FFMPEG = 'ffmpeg'

def main():
    VALID_URLS = {NEWS : r'https?://(?:www\.)?abc\.net\.au/news/(?:[^/]*/){0,}?[0-9]{1,9}',
    TRIPLEJ : r'https?://(?:www\.)?abc\.net\.au/triplej/(?:[^/]*/){0,}?[0-9]{1,9}',
    RADIO: r'https?://(?:www\.)?abc\.net\.au/radio/programs/(?:[^/]*/){0,}?'}
    USAGE_MSG = 'abc_dl [arguments] [article URL]'
    parser = argparse.ArgumentParser(description='Archive ABC (Australian Broadcasting Corporation) News articles.', usage=USAGE_MSG)
    parser.add_argument('-o', dest='output_dir', type=str, help='Output directory for downloaded content.')
    parser.add_argument('-a', '--article', dest='purl', type=str, help='URL of article to download.')
    args = parser.parse_args()

    if(not args.output_dir):
        print('Output directory (-o) is required.')
        sys.exit(USAGE_MSG)
    elif(args.output_dir[-1] == '"' or args.output_dir[-1] == "'"):
        args.output_dir = f'{args.output_dir[:-1]}/'
    elif(args.output_dir[-1] != '/' and args.output_dir[-1] != '\\'):
        args.output_dir += '/'

    if(not os.path.isdir(args.output_dir)):
        try:
            os.mkdir(args.output_dir)
        except:
            sys.exit(f'Could not create directory "{args.output_dir}"')
    
    STYLING_DIR = f'{args.output_dir}styling/'
    if(not os.path.isdir(STYLING_DIR)):
        try:
            os.mkdir(STYLING_DIR)
            os.chdir(os.path.dirname(os.path.realpath(__file__)) + '/utils/')
            for file in glob.glob('*'):
                shutil.copy(os.path.realpath(file), STYLING_DIR)
        except:
            sys.exit(f'Could not create directory "{STYLING_DIR}"')

    if(args.purl):
        for urlmatch in VALID_URLS.items():
            if(bool(re.match(urlmatch[1], args.purl))):
                download_article(args.purl, args.output_dir, urlmatch[0])
                break
    else:
        print('Missing article URL (-a).')
        sys.exit(USAGE_MSG)

def download_article(article_url, output_dir, article_type):
    article_data = BeautifulSoup(get(article_url, allow_redirects=True).text, 'lxml')

    if(article_type == NEWS):
        article_meta = json.loads(article_data.find('script', {'type': 'application/ld+json'}).contents[0])
        _publish_time = create_date(article_data.find('meta', {'property': 'article:published_time'})['content'])
        if(type(article_meta['author']) == list):
            _authors = [author['name'] for author in article_meta['author']]
        else:
            _authors = ['ABC News']
        authorstr = '<p><i>By '
        for index,author in enumerate(_authors):
            authorstr += author
            if(index == len(_authors) - 1):
                authorstr += '.'
            else:
                authorstr += ', '
        authorstr += '</i></p>'

        _title = article_meta['headline']
        header = article_data.find('div', {'data-component': 'FeatureMedia'})
        if(header != None):
            vid = header.find('video')
            if(vid == None):
                _thumbnail = header.find('img')['data-src']
            else:
                _video = vid.find('source')['src']
            try:
                _caption = f'{header.find("figcaption").contents[2]} {header.find("cite").text}'.strip()
            except:
                _caption = header.find('figcaption').text.strip()

        _body = article_data.find('div', {'class': '_3b5Y5 _1BraJ'}).find('div')

        hashed_title = gen_hash_title(_publish_time, _title, _body)
        print(f'Downloading {hashed_title}...')
        _outputfolder = output_dir + f"{hashed_title}/"
        
        if(not os.path.isdir(_outputfolder)):
            os.mkdir(_outputfolder)
        else:
            sys.exit('This article has already been downloaded...')
        if(header != None):
            if(vid == None):
                download_file(_thumbnail, 'thumb.webp', _outputfolder)
            else:
                download_file(_video, 'thumb.mp4', _outputfolder)

        points = _body.find('section', {'aria-label': 'key points'})
        if(points != None):
            _keypoints = [f'<li>{point.text}</li>' for point in points.find_all('li')]
            _keypoints.append('</ul>')
            ul = '<ul>'
            for point in _keypoints:
                ul += f'{point}'
        
        img_index = 1
        vid_index = 1
        element_tree = []
        for element in _body:
            if('class' in element.attrs): # Without this, if an element doesn't have a class, the script will fail.
                if(element['class'] == ['_1HzXw']):
                    element_tree.append(f'<p>{element.text}</p>')
                elif(element['class'] == ['_2w-Eq', '_1w6Cw', '_1pc-9', '_357jP']):
                    video_box = element.find('video')
                    if(video_box == None):
                        image = element.find('img')
                        imgtitle = f'{"{:02d}".format(img_index)}.webp'
                        download_file(image['data-src'], imgtitle, _outputfolder)
                        element_tree.append(f'<img src="{imgtitle}">')
                        img_index += 1
                    else:
                        vidtitle = f'{"{:02d}".format(vid_index)}.mp4'
                        download_file(video_box.find('source')['src'], vidtitle, _outputfolder)
                        element_tree.append(f'<video controls loop autoplay><source src="{vidtitle}" type="video/mp4"/></video>')
                    media_caption = element.find('figcaption')
                    if(media_caption != None):
                        element_tree.append(f'<p><i>{media_caption.text.strip()}</i></p>')

        dochtml = f'<html><head><link rel="stylesheet" href="../styling/abc-style.css"><title>{_title}</title></head><body><h1>{_title}</h1>{authorstr}'
        if(header != None):
            if(vid == None):
                dochtml += f'<img src="thumb.webp"><p><i>'
            else:
                dochtml += f'<video controls loop autoplay><source src="thumb.mp4" /></video>'
            dochtml += f'<p><i>{_caption}</i></p>'

        if(points != None):
            dochtml += f'<div id="key-points"><h3>Key Points</h3>{ul}</div>'
        for element in element_tree:
            dochtml += f'\n{element}'
        dochtml += '</body></html>'
        write_index(_outputfolder, dochtml)
    elif(article_type == TRIPLEJ):
        m3u8_status = False
        from . import triplej
        header = article_data.find('head')
        _title = header.find('meta', {'name': 'title'})['content']
        dochtml = f'<html><head><title>{_title}</title><link rel="stylesheet" href="../styling/abc-style.css"></head><body><h1>{_title}</h1>'
        _publish_time = create_date(header.find('meta', {'name': 'DCTERMS.date'})['content'])
        _body = article_data.find('body')
        hashed_title = gen_hash_title(_publish_time, _title, _body)
        print(f'Downloading {hashed_title}...')
        _outputfolder = output_dir + f"{hashed_title}/"
        if(not check_output_dir(_outputfolder)):
            thumb_content = _body.find('div', {'class': 'img-cont'})
            if(thumb_content.find('script') != None):
                audio_div = _body.find('div', {'id': 'audioPlayerWithDownload5'})
                if(audio_div != None):
                    try:
                        _thumb_audio = audio_div.find('a')['href']
                    except:
                        if(FFMPEG):
                            m3u8_url = triplej.find_m3u8_url(audio_div)
                            m3u8_status = get(m3u8_url).status_code == 200
                            if(m3u8_status):
                                subprocess.run([FFMPEG, '-i', m3u8_url, '-acodec', 'mp3', f'{_outputfolder}thumb.mp3'])
                            else:
                                print('Article audio has expired, using placeholder instead.')
                                _thumb_audio = 'https://www.soundboardguy.com/wp-content/uploads/2021/04/bitconnect.mp3'
                        else:
                            print('This article uses an M3U8 stream to serve its audio, please install ffmpeg in your PATH to download it.')
                            _thumb_audio = 'https://www.soundboardguy.com/wp-content/uploads/2021/04/bitconnect.mp3'
                else:
                    _thumb_video = triplej.find_video_url(thumb_content)
            else:
                _thumb_img = thumb_content.find('img')['src'].replace('thumbnail', 'large')

            article_content = _body.find('div', {'class': 'comp-rich-text article-text clearfix'}).findChildren(recursive=False)

            vid_index = 1
            img_index = 1
            element_tree = []
            if(thumb_content.find('script') != None):
                if(audio_div == None):
                    download_file(_thumb_video, 'thumb.mp4', _outputfolder)
                    dochtml += '<video controls loop autoplay><source src="thumb.mp4" /></video>'
                else:
                    dochtml += '<audio controls loop autoplay><source src="thumb.mp3" /></audio>'
                    if(not m3u8_status):
                        download_file(_thumb_audio, 'thumb.mp3', _outputfolder)
            else:
                download_file(_thumb_img, 'thumb.jpg', _outputfolder)
                dochtml += '<img src="thumb.jpg" >'
            for element in article_content:
                if('class' in element.attrs):
                    if(element['class'] == ['view-embed-full']):
                        continue # Skip related article
                    elif(element['class'] == ['view-inlineMediaPlayer', 'doctype-abcvideo']):
                        vid_title = f'{"{:02d}".format(vid_index)}.mp4'
                        download_file(triplej.find_video_url(element), vid_title, _outputfolder)
                        element_tree.append(f'<video controls autoplay loop><source src="{vid_title}" /></video>')
                        vid_index += 1
                    elif(element['class'] == ['comp-rich-text-blockquote', 'comp-embedded-float-full', 'source-blockquote']):
                        element_tree.append(f'<p><i>{element.text.strip()}</i></p>')
                    elif(element['class'] == ['view-image-embed-full']):
                        img_title = f'{"{:02d}".format(img_index)}.jpg'
                        element_tree.append(f'<img src="{img_title}">')
                        download_file(element.find('img')['src'].replace('thumbnail', 'large'), img_title, _outputfolder)
                        img_index += 1
                else:
                    if(element.name == 'ul' or element.name == 'ol'):
                        ulhtml = '<ul>'
                        ul = [f'<li>{li.text.strip()}</li>' for li in element.find_all('li')]
                        for list_item in ul:
                            ulhtml += list_item
                        ulhtml += '</ul>'
                        element_tree.append(ulhtml)
                    else:
                        element_tree.append(f'<{element.name}>{element.text}</{element.name}>')
            for element in element_tree:
                dochtml += element
            dochtml += '</body></html>'
            write_index(_outputfolder, dochtml)
    elif(article_type == RADIO):
        article_content = BeautifulSoup(get(article_url).text, 'lxml')
        check_playlist = article_content.find('div', {'id': 'collection-program-extras6'})
        if(check_playlist != None):
            for program in check_playlist.find('ul').find_all('li'):
                download_article('https://abc.net.au' + program.find('a')['href'], output_dir, RADIO)
        else:
            _title = article_content.find('h1', {'itemprop': 'name'}).text
            dochtml = f'<html><head><title>{_title}</title><link rel="stylesheet" href="../styling/abc-style.css"></head><body>'
            dochtml += f'<h1>{_title}</h1>'
            thumb = article_content.find('div', {'id': 'audioPlayerWithDownload4'})
            _program_audio = thumb.find('a')['href']
            _thumb_img = thumb.find('img')['src'].replace('thumbnail', 'large')
            hashed_title = gen_hash_title(create_date(article_content.find('meta', {'name': 'DCTERMS.date'})['content']), _title, article_content)
            _outputfolder = output_dir + f"{hashed_title}/"
            if(not check_output_dir(_outputfolder)):
                dochtml += '<img src="thumb.jpg">'
                dochtml += '<audio controls autoplay loop><source src="thumb.mp3"></audio>'

                _article_description = article_content.find('div', {'id': 'comp-rich-text7'})
                text_tree = [text for text in _article_description.contents[1:-1]]
                for text in text_tree:
                    dochtml += str(text)
                dochtml += '</body><html>'
                download_file(_program_audio, 'thumb.mp3', _outputfolder)
                download_file(_thumb_img, 'thumb.jpg', _outputfolder)
                write_index(_outputfolder, dochtml)

def gen_hash_title(published_time, article_title, html):
    escaped_title = article_title.replace(':', '_').replace('?', '_').replace('/', '_').replace('<', '_').replace('>', '_').replace('*', '_').replace('|', '_').replace('\\', '_').replace('"', "'")
    return f"{published_time} - {escaped_title} [{hashlib.md5(html.text.encode('utf-8')).hexdigest()[:6]}]"

def check_output_dir(dir_path):
    if(not os.path.isdir(dir_path)):
        os.mkdir(dir_path)
        return False
    else:
        print('This article has already been downloaded...')
        return True

def create_date(datestr):
    return datestr[:10].replace('-', '')

def write_index(output_folder, html):
    with open(f'{output_folder}index.html', 'w') as f:
            print('Writing index.html...')
            f.write(BeautifulSoup(html, 'lxml').prettify())
            print('Download complete.')

def download_file(url, title, output_dir):
    with open(output_dir + title, 'wb') as f:
        print(f'Downloading {url} as {title}...')
        f.write(get(url).content)
