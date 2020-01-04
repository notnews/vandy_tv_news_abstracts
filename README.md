## Abstracts from Vanderbilt Broadcast TV News Archives 

We provide scripts to scrape and parse the Vanderbilt Broadcast TV News Archives and link to a dataset that includes both the raw files and the parsed data. 

### Final Dataset

Our final parsed dataset is at the program segment level. Each `program` has multiple `broadcast` segments. Each `broadcast` segment gets its own row. The dataset has the following columns:

`date, program_title, program_duration, broadcast_title, broadcast_duration, broadcast_time, broadcast_order, broadcast_abstract, reporter(s)`

#### Data Dictionary

`reporter(s)`: For instance, for this [broadcast](https://tvnews.vanderbilt.edu/broadcasts/16), the reporters are: Cosell, Howard; Reynolds, Frank

`broadcast_time`: For instance, for https://tvnews.vanderbilt.edu/programs/1, the broadcast time for `WORLD SERIES / MCLAIN / GIBSON #16` is `12:20:40 am — 12:22:50 am`

`broadcast_order`: For instance, for https://tvnews.vanderbilt.edu/programs/1, the broadcast time for `WORLD SERIES / MCLAIN / GIBSON #16` is `16`

`broadcast_abstract`: Actual text of the broadcast without the header or footer. 

### Scraping

We start from the [site index](https://tvnews.vanderbilt.edu/siteindex). And then download all the month-year pages.

The `program` and `broadcast` pages rely on a simple counter. So we iterate over all program and broadcast pages. There are a total of 1,119,648 broadcast pages.

We then parse the data to produce the CSV. 

When there is no relevant `broadcast` page, we leave the `broadcast_abstract`, `reporter(s)` fields empty.

## Testing

To make sure, we downloaded all the files, we spot checked existence of various files and compared actual number of links to actual number of files.

## Scripts

[The scripts](vandy/vandy) to scrape and parse are written in Python as a spider using the Scrapy framework.

### Installation

We strongly recommend installing `vandy` inside a Python virtual environment (see [venv documentation](https://docs.python.org/3/library/venv.html#creating-virtual-environments))

    pip install scrapy
    git clone https://github.com/soodoku/vandy_tv_news_abstracts.git

### Run the spider

To scrape all the broadcasts:

    cd  vandy_tv_news_abstracts/vandy
    scrapy crawl vandy_news -o vandy.csv -t csv --loglevel INFO

or you may filter the spider to a specific month using the filter argument:

    cd  vandy_tv_news_abstracts/vandy
    scrapy crawl vandy_news -a filter=2019-11 -o 2019-11.csv -t csv --loglevel INFO

## Final Data

Final data is posted at [Harvard Dataverse](https://doi.org/10.7910/DVN/BP2JXU)

* Raw HTML (`html-vandy.tar.bz2.parta*`)
    To joined them to a file please run ```cat html-vandy.tar.bz2.parta* > html-vandy.tar.bz2```
* Final CSV (`vandy.csv`)

The Scrapy HTTP cache (`httpcach-vandy.tar.bz2`) is also posted. Please extract it to `.scrapy` under the `vandy` folder. Then the spider can use the webpages from the cached data if you don't want to get the live data from the website.

### CSV snippet

|broadcast_abstract                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |broadcast_duration|broadcast_order|broadcast_reporter(s)                               |broadcast_time         |broadcast_title                    |date                  |program_duration|program_title|
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------|---------------|----------------------------------------------------|-----------------------|-----------------------------------|----------------------|----------------|-------------|
|(Studio) Officials of company in soft contact field said chgd. with entertaining officials responsible for regulating the industryREPORTER: Dan Rather(DC) House subcommittee  hearing into claims that soft contact lens users are paying more for cleaning solution due to FDA (Food and Drug Administration) officials Mary Bruch and Arnauld Scafidi making their decisions after lavish entertainment by company mfring. the lens cleaner. [Representative Albert GORE - says evidence indicates Burton, Parsons and Company, Incorporated, adopted corruption of FDA (Food and Drug Administration) officials as company policy.] Testimony of former company official John Bryer with regard to company consultant Keith Whitham's statement that company owner John Tommy Manfuso would make sure Bruch won at the track noted. [BRYER - recalls betting experience.] [WHITHAM - says Bryer is lying.] Manfuso's testimony outlined; new lens cleaning prods. said now allowed on the market after FDA (Food and Drug Administration) transferred authority for approval to other officials.REPORTER: Robert Schakne|00:02:10          |277398         |Rather, Dan;Schakne, Robert                         |05:33:40 pm-05:35:50 pm|Contact Lenses                     |Friday, May 29, 1981  |25 minutes      |CBS Evening News|
|(Baquba: Anderson Cooper)  The frontlines of the fight against the insurgents in Iraq introduced; scenes shown from Baquba.  Technical problems acknowledged.(Baghdad: Christiane Amanpour)  Training the troops in Baghdad featured; scenes shown from Baghdad of the Iraqi troops on a mission in an unarmored truck & walking through the neighborhoods providing security for the elections; details given of the importance of American logistical support.  [Iraqi ENGINEER&nbsp- says when our army is going good so the Americans can leave.]  [Commander Col. Edward CARDON&nbsp- questions an early pullout.]  What makes a good, functioning Iraqi unit discussed.(Baquba: Anderson Cooper)  The frontlines of the fight against the insurgents in Iraq introduced; scenes shown from a patrol by a US unit {2d Platoon, Alpha Battery, Task Force 110} in Baquba; details given about the improved conditions in the city as Iraqi forces get better.  [Capt. Patrick MOFFITT&nbsp- shows a blown-up suicide bomb vehicle.]  The views of the local Iraqis presented.(Baquba: Anderson Cooper; Ramadi: Nic Robertson; Baghdad: Christiane Amanpour)  The situation in different parts of Iraq discussed.|00:13:30          |811919         |Cooper, Anderson;Amanpour, Christiane;Robertson, Nic|09:02:50 pm-09:16:20 pm|Iraq / On Patrol / Iraqi Troops    |Tuesday, Dec 13, 2005 |about 1 hour    |CNN Evening News|
|(Studio) Christmas card from Harry Reasoner and Barbara Walters shown on screen.REPORTER: Harry Reasoner                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |00:00:40          |41423          |Reasoner, Harry                                     |05:26:30 pm-05:27:10 pm|Christmas Greetings                |Friday, Dec 24, 1976  |27 minutes      |ABC Evening News|
|(Studio) Justice William O. Douglas, under fire for "Evergreen" magazine publisher, dismisses self from "I Am Curious Yellow" censorship case; "Evergreen" distributing company handles movie.REPORTER: Howard K. Smith                                                                                                                                                                                                                                                                                                                                                                             |00:00:10          |10130          |Smith, Howard K.                                    |12:08:50 am-12:09:00 am|Douglas / Censorship               |Monday, Apr 27, 1970  |27 minutes      |ABC Evening News|
|                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |00:00:10          |929186         |                                                    |05:48:10 pm-05:48:20 pm|Upcoming Items (Studio: Lester Holt)|Wednesday, Dec 31, 2008|28 minutes      |NBC Evening News|
|(Studio) Govt. reports fuel shortage causes unemployment.REPORTER: John Chancellor                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |00:00:20          |468278         |Chancellor, John                                    |05:36:10 pm-05:36:30 pm|Fuel Shortage / Unemployment       |Thursday, Dec 20, 1973|27 minutes      |NBC Evening News|
|(Studio: Anderson Cooper)  Upcoming item noted.(Studio: Randi Kaye)  A new FBI report on the rise in violent crime in the US; the suspension of basketball player Carmelo Anthony after the Denver Nuggets-New York Knicks brawl on Saturday; a school bus crash in Germantown, Tennessee; & the injury to a stuntman in a show in China, reported; scenes shown of the stuntman hitting a flaming ring while on top of a car.                                                                                                                                                                      |00:01:20          |847387         |Cooper, Anderson;Kaye, Randi                        |09:53:00 pm-09:54:20 pm|360 Bulletin                       |Monday, Dec 18, 2006  |about 1 hour    |CNN Evening News|
|President George W. Bush opens the second day of the Economic Conference  in Washington D.C.Analysis of speech and discussion of "War on Terror" offered by Bill Kristol, editor of "The Weekly Standard" and Fox News Political Analyst.                                                                                                                                                                                                                                                                                                                                                           |00:08:50          |1141931        |                                                    |                       |George W. Bush: Speech at Economic Conference|Thursday, Dec 16, 2004|                |FNC Special  |
|(Studio: Bob Schieffer)  Report introduced.(Vilnius: Cinny Kennard)  Visit by Pope John Paul II to the former Soviet republic of Lithuania featured; scenes shown of the ceremonies in Vilnius, Lithuania.  [Lithuanian WOMAN - comments.] The status of the Roman Catholic Church in the Soviet era and now outlined.  [Reverend Ausvydas BELICKAS - talks about rebuilding.]                                                                                                                                                                                                                      |00:02:10          |352935         |Kennard, Cinny;Schieffer, Bob                       |05:36:30 pm-05:38:40 pm|Lithuania / Pope John Paul II Visit|Saturday, Sep 04, 1993|28 minutes      |CBS Evening News|

When scraping and parsing, we found a few issues. We describe the issues [here](NOTES.md).

## More About the Vanderbilt News Archive

https://en.wikipedia.org/wiki/Vanderbilt_Television_News_Archive
