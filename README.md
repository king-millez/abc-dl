# abc-dl

Archive ABC (Australian Broadcasting Corporation) News articles.

## Supported Article Types

- ABC News
    - Standard articles
- Triple J
  - Like a Version
  - Shows (e.g *Breakfast*, *Hack*, etc)
  - Triple J News

## To do

- Make sure images are scaled correctly

- Scrape the last time the article was updated

- Add link to author's profile (when applicable)

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

### FFmpeg for M3U8 stream downloads (optional)

#### Linux/MacOS

1. Follow instructions [here](https://ostechnix.com/install-ffmpeg-linux/) for your Linux distribution, or [here](http://ericholsinger.com/install-ffmpeg-on-a-mac) for MacOS.

2. Verify installation by running:
    ```sh
    ffmpeg
    ```
    in your terminal.

#### Windows

1. Download [this](https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z) file.

2. Extract it using [7-zip](https://www.7-zip.org/).

3. Navigate to `bin` in the extracted contents:
    ![Extracted 7-zip folder](/.github/img/setup/1.PNG)
    ![Extracted bin folder](/.github/img/setup/2.PNG)
4. Copy `ffmpeg.exe` to a folder you'd like to use, or keep it where it is, it doesn't really matter.
5. Press the *Windows* key on your keyboard, and search for "*environment variables*", open "*Edit the system environment variables*".
    ![Extracted 7-zip folder](/.github/img/setup/3.png)
6. Click "*Environment Variables*", select the "*PATH*" variable, and click "*Edit*".
7. Click "*New*", and then enter the path to the folder where `ffmpeg.exe` is located. (e.g `C:\Users\Millez\ffmpeg`).
8. Test if you've done this correctly by opening a CMD or PowerShell window and running `ffmpeg.exe`
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