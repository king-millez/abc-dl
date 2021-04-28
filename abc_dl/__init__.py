import argparse, sys, os, hashlib, json, re
from requests import get
from bs4 import BeautifulSoup

def main():
    VALID_URL = r'https?://(?:www\.)?abc\.net\.au/news/(?:[^/]+/){2}?[0-9]{9}'
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
    elif(args.output_dir[-1] != '/' or args.output_dir[-1] != '\\'):
        args.output_dir += '/'

    if(not os.path.isdir(args.output_dir)):
        try:
            os.mkdir(args.output_dir)
        except:
            sys.exit(f'Could not create directory "{args.output_dir}"')
    
    if(args.purl):
        if(bool(re.match(VALID_URL, args.purl))):
            download_article(args.purl, args.output_dir)
        else:
            sys.exit('A valid ABC News URL must be used.')
    else:
        print('Missing article URL (-a).')
        sys.exit(USAGE_MSG)

def download_article(article_url, output_dir):
    article_data = BeautifulSoup(get(article_url).text, 'lxml')
    article_meta = json.loads(article_data.find('script', {'type': 'application/ld+json'}).contents[0])

    _publish_time = article_data.find('meta', {'property': 'article:published_time'})['content'][:10].replace('-', '')
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
        _thumbnail = header.find('img')['data-src']
        try:
            _caption = f'{header.find("figcaption").contents[2]} {header.find("cite").text}'.strip()
        except:
            _caption = header.find('figcaption').text.strip()

    _body = article_data.find('div', {'class': '_3b5Y5 _1BraJ'}).find('div')

    hashed_title = f"{_publish_time} - {_title} [{hashlib.md5(_body.text.encode('utf-8')).hexdigest()[:6]}]"
    print(f'Downloading {hashed_title}...')
    _outputfolder = output_dir + f"{hashed_title}/"

    if(not os.path.isdir(_outputfolder)):
        os.mkdir(_outputfolder)
    else:
        sys.exit('This article has already been downloaded...')
    if(header != None):
        download_img(_thumbnail, 'thumb.webp', _outputfolder)

    points = _body.find('section', {'aria-label': 'key points'})
    if(points != None):
        _keypoints = [f'<li>{point.text}</li>' for point in points.find_all('li')]
        _keypoints.append('</ul>')
        ul = '<ul>'
        for point in _keypoints:
            ul += f'{point}'
    
    img_index = 1
    element_tree = []
    for element in _body:
        if('class' in element.attrs): # Without this, if an element doesn't have a class, the script will fail.
            if(element['class'] == ['_1HzXw']):
                element_tree.append(f'<p>{element.text}</p>')
                pass
            elif(element['class'] == ['_2w-Eq', '_1w6Cw', '_1pc-9', '_357jP']):
                image = element.find('img')
                imgtitle = f'{"{:02d}".format(img_index)}.webp'
                download_img(image['data-src'], imgtitle, _outputfolder)
                element_tree.append(f'<img src="{imgtitle}">')
                img_index += 1
    dochtml = f'<html><head><title>{_title}</title></head><body><h1>{_title}</h1>{authorstr}'
    if(header != None):
        dochtml += f'<img src="thumb.webp"><p><i>{_caption}</i></p>'
    if(points != None):
        dochtml += f'<div id="key-points"><h3>Key Points</h3>{ul}</div>'
    for element in element_tree:
        dochtml += f'\n{element}'
    dochtml += '</body></html>'
    with open(f'{_outputfolder}index.html', 'w') as f:
        print('Writing index.html...')
        f.write(dochtml)
        print('Download complete.')

def download_img(url, title, output_dir):
    with open(output_dir + title, 'wb') as f:
        print(f'Downloading {url}...')
        f.write(get(url).content)