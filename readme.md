# Collection of Python Scraper Methods for Logging In And Getting Data

First designed to log into administrative portals (Amazon, Shopify, etc...) and scrape data to be used as visualizer.
Main issue to be solved is to get data from portals without comprehensive API for store metrics.

## Key Features
- Takes a json encoded input
- Navigates to a page and scrapes data from a table. Returns as JSON object.
- Downloads CSV and returns JSON object of CSV data.

## Not Included
- Extensive validation for logging in
- DateTime validation for searching through data by date