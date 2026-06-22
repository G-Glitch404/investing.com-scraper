# Investing.com Scraper

[Open-source](https://github.com/G-Glitch404/investing.com-scraper) actor to scrape Investing.com news articles, analysis pages, article details, images, and structured metadata with flexible filtering and fast bulk extraction.

## Current limitations and downsides of Investing.com Scraper
    - basically it's all performance issues 
* This scraper depends on browser automation so it's a bit slow but very reliable
* Keyword filtering is case-sensitive and can be slow on large runs
* Parallel crawling is limited by site behavior, especially when a single category is sharded across workers
* The Logs tab for every run contains detailed information about the run, including errors, warnings, and debug information, so always check how the crawl is doing though it 

## What does Investing.com Scraper do?

**Investing.com Scraper** is a **high-reliability** Apify Actor for crawling Investing.com content. It can extract news articles, analysis articles, category pages, custom article URLs, all with sentiment analysis, images, article metadata, article bodies, publishers, dates, and tags from Investing.com sections and direct article links.

It is built for structured extraction and for building datasets you can use in analytics, market monitoring, research, archiving, NLP, automation workflows, and financial intelligence.

### Investing.com Scraper can scrape

* News article pages
* Analysis pages
* Category listing pages
* Custom article URLs
* Article images
* Article titles
* Article summaries
* Article categories
* Article publishers
* Publication and update dates
* Full article body text
* Tags and extracted metadata

---

## Why scrape Investing.com?

Investing.com is one of the most visited financial news platforms on the internet and is a valuable source of market-related news, analysis, and article metadata. It is useful for tracking what is happening in finance, crypto, macroeconomics, stocks, and trading.

Here are just some of the ways you could use Investing.com data:

* Daily finance and market monitoring
* Trend detection and market sentiment analysis
* Keyword extraction for trading or marketing opportunities
* Research on financial news cycles and publisher coverage
* Archiving financial articles and analysis
* Training datasets for NLP and machine learning
* Monitoring public reaction to financial events and market moves

If you would like more inspiration on how scraping Investing.com could help your business or organization, check out the [Apify industry pages](https://apify.com/industries).

---

## Supported URL types

You can start the Actor from different kinds of Investing.com URLs. The table below explains what each one does.

| URL example                                              | What the scraper does                         |
|----------------------------------------------------------|-----------------------------------------------|
| `https://www.investing.com/news/latest-news`             | Scrapes latest news listing pages             |
| `https://www.investing.com/news/latest-news/3`           | Scrapes page 3 of latest news                 |
| `https://www.investing.com/news/cryptocurrency-news`     | Scrapes cryptocurrency news listing pages     |
| `https://www.investing.com/news/stock-market-news`       | Scrapes stock market news listing pages       |
| `https://www.investing.com/news/economic-indicators`     | Scrapes economic indicator news listing pages |
| `https://www.investing.com/news/world-news`              | Scrapes world news listing pages              |
| `https://www.investing.com/news/politics`                | Scrapes politics news listing pages           |
| `https://www.investing.com/news/company-news`            | Scrapes company news listing pages            |
| `https://www.investing.com/news/.../article-slug...`     | Scrapes a single article page                 |
| `https://www.investing.com/analysis/.../article-slug...` | Scrapes a single analysis page                |

---

## How to scrape Investing.com

It is easy to use **Investing.com Scraper**.

1. Click on **Try for free**
2. Enter the Investing.com URLs or categories you want to scrape
3. Configure optional filters like keywords, stop date, and field selection
4. Click on **Run**
5. Preview or download your data from the **Dataset** tab

---

## Input reference
    - one must be provided links or categories, but both works too    

| Input                |    Type | Required | Description                                 |
|----------------------|--------:|---------:|---------------------------------------------|
| `links`              |   array |       no | Investing.com URLs to crawl                 |
| `keywords`           |  string |       no | Keyword filtering input used by the scraper |
| `categories`         |   array |       no | Category names to crawl                     |
| `stopDate`           |  string |       no | Earliest allowed article date               |
| `filterFields`       |   array |       no | Drop articles missing selected fields       |
| `maxArticles`        | integer |      yes | Maximum number of articles to collect       |
| `proxyConfiguration` |  object |       no | Apify Proxy or custom proxy settings        |

---

## Input options

## Links

**Type:** array  
**Editor:** `requestListSources`  
**Required:** no  
**Minimum items:** 0  
**Maximum items:** 100

This field is used for Investing.com URLs to scrape from them.

The Actor supports:

* article URLs
* analysis URLs
* category listing URLs
* latest news URLs

### How it behaves

* Each link is processed independently
* The scraper extracts the article or listing content from each URL
* Multiple links can be split across workers automatically
* If a link is a listing page, the Actor crawls articles from that page

### Important notes

* Keep the number of links reasonable if you are scraping large pages
* Large source lists with high article limits can increase runtime
* For large jobs, start with a small number of links first
* If you only need one article, provide a single article URL

### Examples

* One latest-news URL for broad discovery
* One article URL when you need a single page
* Multiple category URLs when you want a topic-wide dataset
* A category URL plus direct article URLs when you want both breadth and depth

---

## Keywords

**Type:** string  
**Editor:** `select`  
**Required:** no

This lets you filter articles by keyword or phrase.

### Examples

* `bitcoin`
* `climate change`
* `fed`
* `earnings`
* `crypto`

### How it works

The Actor keeps only articles that match at least one keyword or phrase, depending on your implementation.

### Best practices

* Use short and specific keyword lists
* Use phrases when you need tighter matching
* Keep the keyword list focused to reduce noisy results
* Combine keywords with stop dates for better dataset relevance

### When to use it

* topic monitoring
* market tracking
* niche content collection
* research around specific financial events
* reducing unnecessary output from broad sources

### Notes

* Keyword matching is case-sensitive
* Empty keyword input disables keyword filtering
* Phrase matching is often better than single generic terms

---

## Categories

**Type:** array  
**Editor:** `select`  
**Required:** yes  
**Minimum items:** 1  
**Maximum items:** 13

This field is used for Investing.com category crawling.

### Supported categories

* all
* general
* latest-news
* popular
* world
* politics
* companies
* stockmarket
* economy
* forex
* trading
* reports
* cryptocurrencies

### Category labels

* `all` → All News & Articles
* `general` → General Daily News
* `latest-news` → Latest News & Articles
* `popular` → Popular Finance News
* `world` → World News
* `politics` → Politics News
* `companies` → Companies News
* `stockmarket` → Stocks Market
* `economy` → Economy News
* `forex` → Forex News
* `trading` → Trading News
* `reports` → Reports Articles
* `cryptocurrencies` → Cryptocurrencies News

### How it behaves

* Each category is processed independently
* The scraper starts from the category listing pages
* Category work can be split automatically across workers
* If only one category is provided, the scraper can shard pages across workers

### Important notes

* Use category names exactly as expected by your scraper
* Multiple categories are distributed across workers automatically
* One category can still be shared across workers using page sharding
* Start with a small number of categories if you are testing

---

## Stop date

**Type:** string  
**Editor:** `datepicker`  
**Optional:** yes

This stops the Actor from returning articles older than the selected date.

### How it behaves

* Only articles published on or after the selected date are collected
* Older articles are skipped
* Leave it empty to crawl without a date limit

### When to use it

* daily monitoring
* recent content collection
* archive reduction
* date-bounded research
* trend snapshots for a specific period

### Example

If you choose `2025-03-01`, the Actor will keep only articles from `2025-03-01` and newer.

### Notes

* Dates are UTC-based
* This is very useful when scraping active categories with large histories

---

## Filter fields

**Type:** array  
**Editor:** `select`  
**Optional:** yes

This option removes articles that are missing selected fields.

### How it works

If you select a field, any article missing that field will be dropped.

Example:

* selecting `title` and `body` keeps only articles that have both fields populated

### Good use cases

* only keep complete articles
* remove sparse or partial records
* ensure data quality before export
* avoid empty or low-value results

### Available fields

* `icon`
* `title`
* `summary`
* `publisher`
* `authors`
* `category`
* `sentiment`
* `sentiment_score`
* `article_type`
* `published`
* `modified`
* `tags`
* `body`
* `url`
* `images`

### Important

This is a strict “must contain all selected fields” filter.

### Practical meaning

* Select nothing to keep all articles
* Select one field to require that field
* Select multiple fields to require all selected fields
* if field Title was selected then articles without Title will be dropped and won't show up 

---

## Maximum articles amount

**Type:** integer  
**Required:** yes  
**Minimum:** 10  
**Maximum:** 10000

This sets the maximum number of articles the Actor will attempt to collect.

### Important behavior

This value is the total target for the run, actor will stop immediately after reaching it without considering any other links or categories it didn't scrape from

### Recommended use

* Use a smaller value for testing
* Use a moderate value for large category runs
* Avoid very large values across many sources unless you know the site is stable

### Why this matters

Investing.com can become unstable if you crawl too aggressively. Parallel workers improve speed, but the site may still throttle or reject some sessions.

### Practical guidance

* `10` to `50` for quick checks
* `100` to `1000` for normal scraping
* Higher values only when you need large archives

---

## Proxy configurations

**Type:** object  
**Editor:** `proxy`  
**Optional:** yes

This controls whether the Actor uses Apify Proxy or a custom proxy setup.

### Recommended use

Use proxies when:

* Investing.com blocks requests
* you see empty or partial results
* you are running larger jobs

### When not to use proxies

* very small test runs
* cases where direct access already works reliably
* if everything is working fine without them

### Notes

* Apify Proxy can help with stability
* Bad proxy settings can reduce reliability
* If requests fail or return blocks, proxies are one of the first things to try

---

## Example input

```json
{
  "links": [
    "https://www.investing.com/news/latest-news",
    "https://www.investing.com/news/cryptocurrency-news"
  ],
  "keywords": "bitcoin",
  "categories": [
    "latest-news",
    "cryptocurrencies"
  ],
  "stopDate": null,
  "filterFields": [
    "title",
    "body",
    "publisher"
  ],
  "maxArticles": 100,
  "proxyConfiguration": {
    "useApifyProxy": false
  }
}
```

---

## Tips for scraping Investing.com

* Use category filtering to focus on relevant market sections
* Use custom links when you need specific pages or direct articles
* Start with a small `maxArticles` value first
* Use `filterFields` to remove incomplete or noisy records
* Use `stopDate` when you only need recent articles
* Use proxies if you encounter blocks, empty pages, or unstable runs
* Keep keyword filtering focused because it is case-sensitive and slower

---

## Cost considerations

Apify includes free usage credits on the Free plan, and the final cost depends on:

* number of articles scraped
* number of category pages or article pages visited
* amount of browser runtime
* proxy usage
* worker count
* retry count and failed sessions

For lighter scraping tasks, this Actor can be used efficiently with small batches of categories or URLs. For larger monitoring, research, or archival jobs, a paid Apify plan is recommended.

---

## Is it legal to scrape Investing.com?

Scraping publicly available data may be legal, but you should always review the website’s terms of service and applicable laws before collecting data at scale.

Personal data may be protected by GDPR and other privacy regulations. Do not scrape personal data unless you have a legitimate reason to do so.

If you are unsure, consult a lawyer.

We also recommend reading Apify’s article: [Is web scraping legal?](https://blog.apify.com/is-web-scraping-legal/)

---

## Contact me

If you have suggestions, bug reports, or feature requests, feel free to open an issue or contact me through [GitHub](https://github.com/G-Glitch404).

---

## More scrapers

* [The Ultimate News Scraper](https://apify.com/glitch_404/ultimate-news-scraper)
* [Light-Weight Reddit Scraper](https://apify.com/glitch_404/redditscraper)
