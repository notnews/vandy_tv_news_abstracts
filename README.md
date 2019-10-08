# Abstracts from Vanderbilt Broadcast TV News Archives 

Base URL: https://tvnews.vanderbilt.edu/siteindex

## Scraping

Download all broadcast pages ala: https://tvnews.vanderbilt.edu/broadcasts/84165

To do that:

1. Iterate over the site-index to get all the months
2. Within each month, iterate over each channel-day
3. And within each channel day, iterate over each broadcast

When downloading, we need to put it in an organized way: 
* Store all month pages under monthly-pages
* Store all broadcast pages under broadcast

Create a CSV with metadata that links each broadcast to all the relevant file names, which is =
broadcast_id (which will be the same as the filename and hence allow us to build a relative URL to it; where there is 'no broadcast', it is left as empty), channel, date, month-page-name (e.g., 1983-5, which will allow us to build a relative URL to month-page), channel-date-list (list of all the broadcasts)

## Parsing

Parse the webpages into a broadcast level dataset which we will then concatenate to a program-date level dataset.

broadcast level data =

broadcast_id, abstract_text (without the blurb at top and bottom and cleans out html etc. but keeps paragraph and line breaks), duration, reporter(s), channel, date, program_name (e.g., CBS Evening News for Sunday), ...

## Testing

To make sure, we downloaded all the files, we spot checked existence of various files and compared actual number of links to actual number of files.

## Scripts

1. Scraping
2. Parsing

## Final Data

1. Raw HTML
2. Final CSV












* 

