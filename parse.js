const axios = require('axios');
const cheerio = require('cheerio');
const fs = require('fs'); 

async function scrapeKorupediaDetail() {
    const url = 'data/data_100.html'; //contoh

    try {
        const html = fs.readFileSync(url, 'utf8');
        const $ = cheerio.load(html);

        const scrapedData = {};

        scrapedData.nama = $('.nama-hakim').text().trim();
        scrapedData.deskripsi = $('.entry-title').next('p').text().trim();

        const tableRows = $('.content-body table tbody tr');
        tableRows.each((index, element) => {
            const cells = $(element).find('td');
            if (cells.length === 2) {
                const key = $(cells[0]).text().trim().replace(/ /g, '_').toLowerCase(); // Format key for object
                const value = $(cells[1]).text().trim();
                scrapedData[key] = value;
            }
        });

        console.log('Data scraped successfully:');
        console.log(scrapedData);

        // opsional
        // fs.writeFileSync('koruptor_data.json', JSON.stringify(scrapedData, null, 2));
        // console.log('Data saved to koruptor_data.json');

        return scrapedData;

    } catch (error) {
        console.error('Error during scraping:', error.message);
        return null;
    }
}

scrapeKorupediaDetail();