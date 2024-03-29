import json
import os
import sys
import urllib

from bs4 import BeautifulSoup
import requests


class Google:
    def __init__(self):
        self.GOOGLE_SEARCH_URL = 'https://www.google.co.jp/search'
        self.session = requests.session()
        self.session.headers.update(
            {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0'})

    def search(self, keyword, maximum):
        print('begin searching', keyword)
        query = self.query_gen(keyword)
        return self.image_search(query, maximum)

    #検索キーワードからクエリ付与したURLを生成
    def query_gen(self, keyword):
        # search query generator
        page = 0
        while True:
            params = urllib.parse.urlencode({
                'q': keyword,
                'tbm': 'isch',#画像検索を指定
                'ijn': str(page)})

            yield self.GOOGLE_SEARCH_URL + '?' + params
            page += 1

    #画像検索のURL(query_gen)と画像取得枚数(maximum)を指定
    def image_search(self, query_gen, maximum):
        # search image
        result = []
        total = 0
        while True:
            # search
            html = self.session.get(next(query_gen)).text #画像検索結果ページのhtmlを取得
            soup = BeautifulSoup(html, 'lxml')
            elements = soup.select('.rg_meta.notranslate') #指定したクラスを全て取得
            jsons = [json.loads(e.get_text()) for e in elements] #取得したクラスから要素を取得しjson→辞書形式に変換
            imageURLs = [js['ou'] for js in jsons] #画像のURLを取得

            # add search result
            if not len(imageURLs):
                print('-> no more images')
                break
            elif len(imageURLs) > maximum - total:
                result += imageURLs[:maximum - total]
                break
            else:
                result += imageURLs
                total += len(imageURLs)

        print('-> found', str(len(result)), 'images')
        return result


def main():
    google = Google()
    # error
    if len(sys.argv) != 3:
        print('invalid argment')
        print('> ./image_collector_cui.py [target name] [download number]')
        sys.exit()
    else:
        # save location
        name = sys.argv[1]
        data_dir = 'data/'
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs('data/' + name, exist_ok=True)

        # search image
        result = google.search(
            name, maximum=int(sys.argv[2]))

        # download
        download_error = []
        for i in range(len(result)):
            print('-> downloading image', str(i + 1).zfill(4))
            try:#画像をダウンロードしてローカルに保存
                urllib.request.urlretrieve(
                    result[i], data_dir + name + '/' + str(i + 1).zfill(4) + '.jpg')
            except:
                print('--> could not download image', str(i + 1).zfill(4))
                download_error.append(i + 1)
                continue

        print('complete download')
        print('├─ download', len(result)-len(download_error), 'images')
        print('└─ could not download', len(
            download_error), 'images', download_error)


if __name__ == '__main__':
    main()
