import requests
from bs4 import BeautifulSoup
import expanddouban
import  csv
import codecs

def getMovieurl(category, location):
    url = 'https://movie.douban.com/tag/#/?sort=S&range=9,10&tags=电影,' + category +',' + location
    html = expanddouban.getHtml(url)
    return html

def parse_movie(html,category,location):
    global movies
    soup = BeautifulSoup(html, 'html.parser')
    movie_lists = soup.find(class_= 'list-wp').find_all('a', recursive = False)
    for movie in movie_lists:
        movie_name = movie.find(class_ = 'title').string
        movie_rate = movie.find(class_ = 'rate').string
        movie_location = location
        movie_category = category
        movie_info_link = movie['href']
        movie_cover_link = movie.find('img').get('src')
        movies.append(Movie(movie_name, movie_rate, movie_location, movie_category, movie_info_link,movie_cover_link).print_data())

class Movie:
    def __init__(self, name, rate, location, category, info_link, cover_link):
        self.name = name
        self.rate = rate
        self.location = location
        self.category = category
        self.info_link = info_link
        self.cover_link = cover_link
    def print_data(self):
        return('{}|{}|{}|{}|{}|{}'.format(self.name,self.rate,self.location,self.category,self.info_link,self.cover_link))

def save_to_file(content):
    with open('movies.csv', 'w', encoding = 'utf_8_sig', newline = "") as f:
        writer = csv.writer(f)
        for m in content:
            writer.writerow(m.split('|'))

def get_location():
    location_list = []
    url = 'https://movie.douban.com/tag/#/?sort=S&range=9,10&tags=电影'
    html = expanddouban.getHtml(url)
    soup = BeautifulSoup(html, 'html.parser')
    for tag in  soup.find(class_ = 'tags').find_all(class_ = 'category'):
        if tag.find(class_="tag-checked tag").get_text() == '全部地区':
            for loc in tag.find(class_="tag-checked tag").parent.next_siblings:
                 location_list.append(loc.get_text())
    return location_list

def analysis_movie_category():
    global movies
    cat_dict = {}
    for m in movies:
        m = m.split('|')
        if m[3] not in cat_dict :
            cat_dict[m[3]] = {}
        if m[2] not in cat_dict[m[3]]:
            cat_dict[m[3]][m[2]] = 1
        else:
            cat_dict[m[3]][m[2]] += 1
    print(cat_dict)
    return cat_dict

def max_movie_num(cat_dict,n):
    with open('output.txt', 'w', encoding = 'utf_8_sig') as f:
        for key, value  in cat_dict.items():
            num = 0
            for k,v in value.items():
                num += v
            top3 = sorted(value.items(), key=lambda x: x[1], reverse=True)[0:n]
            print(key + str(num) + '部' + ':')
            f.write(key + str(num) + '部' + ':' + '\n')
            for each in top3:
                print("  " + each[0] + '有' + str(each[1]) + '部电影, 占比' + str(round((each[1]/num)*100,1)) + '%')
                print('+ {} + 有 + {} + 部电影, 占比 + {:.2%} + %'.format(each[0], each[1], each[1]/num))
                f.write(' {}有{}部电影, 占比{:.2%}\n'.format(each[0], each[1], each[1] / num))

def main():
    global movies
    movies = []
    n = 1
    category_list = ['喜剧', '科幻', '悬疑']
    location_list = get_location()
    for cat in category_list:
        for loc in location_list:
            print('正在获取' + loc + cat + '电影')
            html = getMovieurl(cat,loc)
            parse_movie(html,cat,loc)
    category_list = analysis_movie_category()
    max_movie_num(category_list, n)
    save_to_file(movies)

if __name__ == '__main__':
    main()
