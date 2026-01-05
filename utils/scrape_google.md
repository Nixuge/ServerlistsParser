# Scrape google
Scraping google can be useful to get links for the textfile and labymodtext parsers.

For that, first run `bun run receiver.ts`

Then, search for something, like:
- `site:https://namemc.com/server/`
- `site:https://laby.net/server/`

And simply copy the code in [scrapegoogle.js](./scrapegoogle.js) and paste it in your console, then up arrow every refresh until you're at the last page.

You should now have all of the google results in `output.txt`