# setwd
setwd(githubdir)
setwd("vandy_tv_news_abstracts/")

# Load libs
library(xml2)
library(rvest)

# Domain 
domain <- "https://tvnews.vanderbilt.edu"

# Read main page
vandy <- read_html(paste0(domain, "/siteindex"))

# Links to webpages for each month/year
month_year <- vandy %>% 
  html_nodes("a") %>% 
  html_attr("href")

month_year <- month_year[9:624]
month_year <- paste0(domain, month_year)


