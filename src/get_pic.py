# h1 .entry-title nama-hakim untuk nama koruptor
# .tbl-clean->tbody->tr->td widht='20%' foto koruptor
# .content-body parse aja nnti datanya di pick lagi

from bs4 import BeautifulSoup

# starts from data_11.html

html = """
<table class="tbl-clean">
    <tbody>
        <tr>
            <td width="20%"><a href="https://example.com">Link Text</a></td>
            <td>Other Data</td>
        </tr>
        <tr>
            <td width="20%"><a href="https://another.com">Another Link</a></td>
            <td>More Data</td>
        </tr>
    </tbody>
</table>
"""

with open("data/htm")

soup = BeautifulSoup(html, 'lxml')

table = soup.find('table', class_='tbl-clean')
if not table:
    print("Table with class 'tbl-clean' not found!")
    exit()

tbody = table.find('tbody')
if not tbody:
    print("No tbody found in the table!")
    exit()

rows = tbody.find_all('tr')

links = []
for row in rows:
    td = row.find('td', attrs={'width': '20%'})
    if td:
        link = td.find('a')
        if link and link.get('href'):
            links.append(link['href'])

if links:
    print("Found links:")
    for i, link in enumerate(links, 1):
        print(f"{i}. {link}")
else:
    print("No links found in the specified <td> elements.")
