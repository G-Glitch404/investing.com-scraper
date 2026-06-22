# Changelog

All notable changes to the project will be documented in this file.

---

# Version 2.0.0

Major rewrite and modernization of the scraper.

## Added

### Flexible inputs

* Added support for scraping from both category names and custom URLs simultaneously
* Added keyword filtering
* Added article field filtering
* Added stop date support
* Added support for proxy configuration
* Added support for dynamic request lists

### New extracted fields

* Authors
* Summary
* Tags
* Modified date
* Multiple images
* Article type
* Sentiment
* Sentiment score

### Dataset improvements

* Added Overview dataset schema
* Improved dataset formatting
* Added proper image rendering
* Added array formatting for authors, tags, and images
* Added date formatting for published and modified dates
* Added clickable URLs

### Crawling improvements

* Introduced worker architecture
* Added parallel crawling
* Added automatic work distribution
* Added automatic article limit distribution between workers
* Added category page sharding
* Added support for mixing links and categories in a single run
* Improved scalability

### Database improvements

* Added database rebuild logic
* Added automatic cleanup before runs
* Improved article deduplication
* Improved article insertion flow

### Filtering improvements

* Added missing field filtering
* Added category validation
* Added keyword filtering
* Improved article validation

### Performance improvements

* Improved crawling speed
* Improved workload balancing
* Reduced duplicated work
* Improved large runs
* Better handling of thousands of articles

### Logging improvements

* More detailed logs
* Worker startup logs
* Better error reporting
* Better progress information

### Documentation

* Completely rewritten README
* Added detailed input documentation
* Added dataset documentation
* Added output examples
* Added supported category descriptions

---

# Changed

### Internal architecture

* Reorganized the project structure
* Refactored the crawling manager
* Refactored worker execution
* Simplified work distribution logic
* Improved code maintainability

### Article model

The article model was expanded from:

* Image
* Title
* Category
* Publisher
* Date
* Link
* Comments
* Paragraph

To:

* Icon
* Title
* Summary
* Publisher
* Authors
* Category
* Sentiment
* Sentiment Score
* Article Type
* Published
* Modified
* Tags
* Body
* URL
* Images

### Input schema

* Redesigned the Actor input schema
* Improved descriptions and examples
* Added stronger validation
* Added better defaults

### Output schema

* Introduced dataset views
* Added formatting for images and dates
* Improved dataset readability

---

# Removed

### Comments extraction

Removed:

* Comment count
* Article comments
* Comment replies

Reason:

* Greatly slowed down the scraper
* Increased complexity
* Increased request count
* Increased headache for me

### Old architecture

Removed:

* Monolithic crawler behavior
* Single-worker assumptions
* Older input model

---

# Performance

## Version 1.0

* Single crawler
* Limited filtering
* unreliable and broke after investing.com updated their protection and UI

## Version 2.0

* Parallel workers
* Dynamic workload distribution
* Category sharding
* Better scaling
* Increased reliability
* Lower overhead

---

# Version 2.0

Initial release.

## Features

* Scraped Investing.com news articles
* Extracted article body
* Built-in sentiment analysis
* Exported to JSON, XML, CSV, HTML and Excel
* Date range support
* Category crawling
* Basic article metadata extraction
* No proxies required
* Parallel workers
* Dynamic workload distribution
