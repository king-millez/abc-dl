# abc-dl

Archive ABC (Australian Broadcasting Corporation) News articles.

## To do

- Add ability to download videos embedded in an article

- Add global CSS file to style articles in a more visually appealing way

- Make sure images are scaled correctly

- Scrape the last time the article was updated

- Add support for older articles before the ABC's website upgrade, and support for articles written before the upgrade before that (they're very busy).

## Setup

1. Clone repository
    ```sh
    git clone https://github.com/king-millez/abc-dl
    ```
2. Enter cloned repository
    ```sh
    cd abc-dl
    ```
3. Install `poetry`
    ```sh
    pip3 install poetry
    ```
4. Update/install project dependencies
    ```sh
    poetry update
    ```

## Usage

1. Go find an article to download, copy its URL (e.g: [this one](https://www.abc.net.au/news/2021-04-28/super-pink-moon-shines-across-australia/100099278)).
2. Download it like this:
    ```sh
    poetry run python3 -m abc_dl -o '~/Desktop/ABC/' -a 'https://www.abc.net.au/news/2021-04-28/super-pink-moon-shines-across-australia/100099278'
    ```

This will output a directory with the title of the article and the first 6 characters of its unique MD5 hash, so if the article is updated you'll be able to save multiple versions without conflicts.

![Screenshot of folder](/.github/img/1.PNG)
![Screenshot of inside folder](/.github/img/2.PNG)

Open `index.html` in a browser to view the offline, compressed article:

![Screenshot of article](/.github/img/3.PNG)