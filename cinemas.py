from bs4 import BeautifulSoup
import requests
import re
import operator

def fetch_afisha_page():
    response = requests.get('http://www.afisha.ru/msk/schedule_cinema/')
    return response.text


def parse_afisha_list(raw_html):
    html_doc = BeautifulSoup(raw_html, 'html.parser')
    for tag in html_doc.find_all('div', class_='m-disp-table'):
        movie_title = tag.h3.a.string
        timetable = tag.find_next('table')
        cinema_count = len(timetable.find_all('td', class_='b-td-item'))
        yield (movie_title, cinema_count)


def fetch_movie_info(movie_title):
    search_url = 'https://www.kinopoisk.ru/index.php'
    get_params = {
        'first': 'no',
        'kp_query': movie_title
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:50.0)'\
            ' Gecko/20100101 Firefox/50.0'
    }
    response = requests.get(
        search_url,
        params=get_params,
        timeout=10,
        headers=headers
    )
    html_doc = BeautifulSoup(response.content, 'html.parser')
    tag = html_doc.find('div', class_='most_wanted')
    indicators = ['0', '0']
    if tag.div.div:
        title = tag.div.div['title']
        indicators = re.sub(r'[^0-9\.(]','', title).split('(')
        if not indicators[0]:
            indicators[0] = tag.div.div.string
    rating = float(indicators[0])
    votes_count = int(indicators[1])

    return rating, votes_count


def output_movies_to_console(movies, count):
    for movie in movies.sort(key=operator.itemgetter(2, 3))[:count]:
        print(movie[0])
        print(' - rating: {0}'.format(movie[1]))
        print(' - votes count: {0}'.format(movie[2]))
        print(' - cinema count: {0}'.format(movie[3]))


if __name__ == '__main__':
    movies = []
    for movie_title, cinema_count in parse_afisha_list(fetch_afisha_page()):
        rating, votes_count = fetch_movie_info(movie_title)
        movies.append([movie_title, rating, votes_count, cinema_count])
    output_movies_to_console(movies, 10)