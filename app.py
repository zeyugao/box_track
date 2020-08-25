import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template
from flask import request

app = Flask(__name__)


@app.route('/get_box_office')
def get_box_office():
    url = request.args.get('url')
    if url is None or not url.startswith('https://www.boxofficemojo.com/'):
        return render_template('get_box_office.html', error='Arg invalid'), 400
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, features='html.parser')

    summary = []

    summary_sections = soup \
        .find('div', {'class': 'mojo-performance-summary-table'}) \
        .find_all('div',
                  {'class': 'a-section'})
    for section in summary_sections:
        loc = section.find('span', {'class': 'a-size-small'}).text.strip()
        money = section.find('span', {'class': 'money'}).text.strip()
        summary.append((loc, money))

    movie_name = soup.find('h1', attrs={'class': 'a-size-extra-large'}).text
    tables = soup.find_all('table')
    results = []
    for table in tables:
        trs = table.find_all('tr')
        for tr in trs[1:]:
            tds = tr.find_all('td')
            place = tds[0].a.text.strip()
            release_date = tds[1].text.strip()
            opening = tds[2].text.strip()
            gross = tds[3].text.strip()
            results.append((place, release_date, opening, gross))

    return render_template(
        'get_box_office.html',
        summary=summary,
        movie_name=movie_name,
        results=results
    )


if __name__ == '__main__':
    app.run()
