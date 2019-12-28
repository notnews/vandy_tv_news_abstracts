## Abstracts from Vanderbilt Broadcast TV News Archives 

We provide scripts to scrape and parse the Vanderbilt Broadcast TV News Archives and link to a dataset that includes both the raw files and the parsed data. 

### Final Dataset

Our final parsed dataset is at the program segment level. Each `program` has multiple `broadcast` segments. Each `broadcast` segment gets its own row. The dataset has the following columns:

`date, program_title, program_duration, broadcast_title, broadcast_duration, broadcast_time, broadcast_order, broadcast_abstract, reporter(s)`

#### Data Dictionary

`reporter(s)`: For instance, for this [https://tvnews.vanderbilt.edu/broadcasts/16](broadcast), the reporters are: Cosell, Howard; Reynolds, Frank

`broadcast_time`: For instance, for https://tvnews.vanderbilt.edu/programs/1, the broadcast time for `WORLD SERIES / MCLAIN / GIBSON #16` is `12:20:40 am — 12:22:50 am`

`broadcast_order`: For instance, for https://tvnews.vanderbilt.edu/programs/1, the broadcast time for `WORLD SERIES / MCLAIN / GIBSON #16` is `16`

`broadcast_abstract`: Actual text of the broadcast without the header or footer. 

### Scraping

We start from the [https://tvnews.vanderbilt.edu/siteindex](site index). And then download all the month-year pages.

The `program` and `broadcast` pages rely on a simple counter. So we iterate over all program and broadcast pages. There are a total of 1,143,009 program pages and a total of 1,143,022 broadcast pages.

We then parse the data to produce the CSV. 

When there is no relevant `broadcast` page, we leave the `broadcast_abstract`, `reporter(s)` fields empty.

## Testing

To make sure, we downloaded all the files, we spot checked existence of various files and compared actual number of links to actual number of files.

## Scripts

1. [Scraping]()
2. [Parsing]()
3. [Testing]()

## Final Data

Final data posted at [https://doi.org/10.7910/DVN/BP2JXU](Harvard Dataverse)

* Raw HTML 
* Final CSV

CSV snippet

```


```

## More About the Vanderbilt News Archive

https://en.wikipedia.org/wiki/Vanderbilt_Television_News_Archive



* 

