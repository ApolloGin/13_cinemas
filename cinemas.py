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
    rating, votes_count = get_data_from_html_page(html_doc)

    return rating, votes_count


def get_data_from_html_page(html_doc):
    tag = html_doc.find('div', class_='most_wanted')
    rating = '0'
    votes_count = '0'
    if tag.div.div:
        str_with_data = tag.div.div['title']
        str_with_data = re.sub(
            r'[^0-9\.(]',
            '',
            str_with_data
        )
        rating, votes_count = str_with_data.split('(')

        if not rating:
            rating = tag.div.div.string

    return float(rating), int(votes_count)



def output_movies_to_console(movies, count):
    sorted_movies = sorted(
        movies,
        key=operator.itemgetter(1, 2),
        reverse=True
    )
    for movie in sorted_movies[:count]:
        print(movie[0])
        print(' - rating: {0}'.format(movie[1]))
        print(' - votes count: {0}'.format(movie[2]))
        print(' - cinema count: {0}'.format(movie[3]))


if __name__ == '__main__':
    movies = []
    for movie_title, cinema_count in parse_afisha_list(fetch_afisha_page()):
        rating, votes_count = fetch_movie_info(movie_title)
        print([movie_title, rating, votes_count, cinema_count])
        movies.append([movie_title, rating, votes_count, cinema_count])
    output_movies_to_console(movies, 10)