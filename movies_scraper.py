from bs4 import BeautifulSoup
import requests
import time
import csv

movies_links = []
movie_data = []

for single_page in range(int(11897/250)):
    broken = False
    page = requests.get(
        'https://www.imdb.com/search/title/?title_type=feature&release_date=2015-01-01,2019-11-13&sort=' +
        'boxoffice_gross_us,asc&count=250&start=' + str(single_page*250 + 1) + '&ref_=adv_nxt')

    soup = BeautifulSoup(page.text, 'html.parser')
    movies = soup.find_all(class_='lister-item mode-advanced')

    for movie in movies:
        movie_href = movie.find(class_='lister-item-image float-left').find('a')['href']
        single_movie = movie.find(class_="sort-num_votes-visible").find_all('span', {"name": "nv"})

        # conditional statement to exclude movies without known box office
        if str(single_movie[0].contents[0][0]) == '$':
            movies_links.append(movie_href)
        else:
            try:
                if str(single_movie[1].contents[0][0]) == '$':
                    movies_links.append(movie_href)
                else:
                    broken = True
                    print("Unknown Error")
            except IndexError:
                broken = True
                break
    if broken:
        break
    time.sleep(1)


def fetch_movie_data(href):
    page2 = requests.get('https://www.imdb.com' + str(href))
    soup2 = BeautifulSoup(page2.text, 'html.parser')
    movie_details = soup2.find(id="titleDetails")
    info = {'link': href, 'box_office': 'NA', 'budget': 'NA', 'in_english': 'NA', 'runtime': 'NA',
            'critics_score': 'NA', 'is_genre_action': '0', 'is_genre_adventure': '0', 'is_genre_animation': '0',
            'is_genre_biography': '0', 'is_genre_comedy': '0', 'is_genre_crime': '0', 'is_genre_documentary': '0',
            'is_genre_drama': '0', 'is_genre_family': '0', 'is_genre_fantasy': '0', 'is_genre_film-noir': '0',
            'is_genre_game-show': '0', 'is_genre_history': '0', 'is_genre_horror': '0', 'is_genre_music': '0',
            'is_genre_musical': '0', 'is_genre_mystery': '0', 'is_genre_news': '0', 'is_genre_reality-tv': '0',
            'is_genre_romance': '0', 'is_genre_sci-fi': '0', 'is_genre_sport': '0', 'is_genre_talk-show': '0',
            'is_genre_thriller': '0', 'is_genre_war': '0', 'is_genre_western': '0'}
    try:
        textblocks = movie_details.find_all(class_="txt-block")
        for t in textblocks:
            try:
                header = t.find(class_="inline").contents
                if 'Cumulative Worldwide Gross' in str(header[0]):
                    info['box_office'] = str(t.contents[2]).replace(' ', '').replace('\n', '')
                elif 'Budget' in str(header[0]):
                    info['budget'] = str(t.contents[2]).replace(' ', '').replace('\n', '')
                elif 'Language' in str(header[0]):
                    for lang in t.find_all('a'):
                        if 'English' in str(lang.contents[0]):
                            info['in_english'] = 1
                    if info['in_english'] == 'NA':
                        info['in_english'] = 0
                elif 'Runtime' in str(header[0]):
                    info['runtime'] = str(t.find('time').contents[0])

            except AttributeError:
                pass

    except ValueError:
        pass

    try:
        movie_storyline = soup2.find(id="titleStoryLine")
        textblocks = movie_storyline.find_all(class_="see-more inline canwrap")
        try:
            for genre in textblocks[1].find_all('a'):
                if 'is_genre_{}'.format(genre.contents[0].lower()[1:]) in info.keys():
                    info['is_genre_{}'.format(genre.contents[0].lower()[1:])] = 1
                else:
                    print('Error in movie ' + href + ' unknown genre')

        except IndexError:
            print('Error in movie ' + href + ' no genres')

    except ValueError or IndexError:
        print('value/index error')

    try:
        movie_review = soup2.find(class_="metacriticScore score_mixed titleReviewBarSubItem").find('span')
        info['critics_score'] = movie_review.contents[0]

    except AttributeError:
        pass

    time.sleep(1)
    if 'NA' not in info.values():
        movie_data.append(info)
    return


print('List of movies ready. Starting to scrap data...')
informational_number = 1
for link in movies_links:
    fetch_movie_data(link)
    print('Scraped ', informational_number, ' of ', len(movies_links), ' movies - ',
          ('%.3f' % (informational_number/len(movies_links)*100)), '% ')
    informational_number += 1
print('Preparing CSV file...')

with open('movies_data.csv', mode='w') as csv_file:
    fieldnames = ['link', 'box_office', 'budget', 'in_english', 'runtime', 'critics_score', 'is_genre_action',
                  'is_genre_adventure', 'is_genre_animation', 'is_genre_biography', 'is_genre_comedy', 'is_genre_crime',
                  'is_genre_documentary', 'is_genre_drama', 'is_genre_family', 'is_genre_fantasy', 'is_genre_film-noir',
                  'is_genre_game-show', 'is_genre_history', 'is_genre_horror', 'is_genre_music', 'is_genre_musical',
                  'is_genre_mystery', 'is_genre_news', 'is_genre_reality-tv', 'is_genre_romance', 'is_genre_sci-fi',
                  'is_genre_sport', 'is_genre_talk-show', 'is_genre_thriller', 'is_genre_war', 'is_genre_western']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for row in movie_data:
        writer.writerow(row)
