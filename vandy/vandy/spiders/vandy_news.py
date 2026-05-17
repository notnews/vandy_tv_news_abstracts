# -*- coding: utf-8 -*-

import os
import re
import gzip
import logging
from datetime import datetime, date, timedelta
from urllib.parse import urljoin

import scrapy
from scrapy.exceptions import CloseSpider
from tqdm import tqdm


class VandyNewsSpider(scrapy.Spider):
    name = 'vandy_news'
    allowed_domains = ['tvnews.vanderbilt.edu']
    start_urls = ['https://tvnews.vanderbilt.edu/siteindex/']
    
    # Configuration
    custom_settings = {
        'DOWNLOAD_DELAY': 1,  # Be respectful to the server
        'RANDOMIZE_DOWNLOAD_DELAY': 0.5,
        'CONCURRENT_REQUESTS': 8,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 10,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 2.0,
    }
    
    # Directory structure
    BASE_DIR = './html'
    BROADCASTS_DIR = './html/broadcasts'
    PROGRAMS_DIR = './html/programs'
    
    def __init__(self, *args, **kwargs):
        super(VandyNewsSpider, self).__init__(*args, **kwargs)
        self.setup_directories()
        self.setup_temporal_filtering()
        self.filter = getattr(self, 'filter', None)
        self.max_items = int(getattr(self, 'max_items', 0))  # 0 means no limit
        self.items_scraped = 0
        self.total_months = 0
        self.months_processed = 0
        self.total_broadcasts_expected = 0
        self.broadcasts_processed = 0
        self.pbar_months = None
        self.pbar_broadcasts = None
        
    def setup_directories(self):
        """Create necessary directories if they don't exist."""
        directories = [self.BASE_DIR, self.BROADCASTS_DIR, self.PROGRAMS_DIR]
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                self.logger.info(f'Created directory: {directory}')
                
    def setup_temporal_filtering(self):
        """Configure temporal boundaries for scraping."""
        # Parse end_date parameter or default to today
        end_date_str = getattr(self, 'end_date', None)
        if end_date_str:
            self.end_date = self._parse_date_string(end_date_str)
            if self.end_date:
                self.logger.info(f'Using specified end date: {self.end_date}')
            else:
                self.logger.warning(f'Invalid end_date format: {end_date_str}, using today')
                self.end_date = date.today()
        else:
            self.end_date = date.today()
            self.logger.info(f'Using current date as end boundary: {self.end_date}')
            
        # Parse start_date parameter for temporal range
        start_date_str = getattr(self, 'start_date', None)
        if start_date_str:
            if start_date_str.lower() == 'today':
                self.start_date = date.today()
                self.logger.info(f'Using today as start date: {self.start_date}')
            else:
                self.start_date = self._parse_date_string(start_date_str)
                if self.start_date:
                    self.logger.info(f'Using specified start date: {self.start_date}')
                else:
                    self.logger.warning(f'Invalid start_date format: {start_date_str}, no start boundary')
                    self.start_date = None
        else:
            self.start_date = None
            
        # Allow buffer for recent content (some archives have delay)
        buffer_days = int(getattr(self, 'buffer_days', 0))
        if buffer_days > 0:
            self.end_date = self.end_date - timedelta(days=buffer_days)
            self.logger.info(f'Applied buffer: scraping until {self.end_date}')
            
    def _parse_date_string(self, date_str):
        """Parse date string using common formats."""
        if not date_str:
            return None
            
        # Common date formats to try
        formats = [
            '%Y-%m-%d',     # 2024-01-15
            '%Y/%m/%d',     # 2024/01/15
            '%m/%d/%Y',     # 01/15/2024
            '%m-%d-%Y',     # 01-15-2024
            '%Y-%m',        # 2024-01
            '%Y/%m',        # 2024/01
            '%Y%m%d',       # 20240115
            '%d-%m-%Y',     # 15-01-2024
            '%d/%m/%Y',     # 15/01/2024
        ]
        
        for fmt in formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt).date()
                return parsed_date
            except ValueError:
                continue
                
        # Try to parse partial dates (year only, year-month)
        if date_str.isdigit() and len(date_str) == 4:
            try:
                year = int(date_str)
                return date(year, 1, 1)
            except ValueError:
                pass
                
        return None

    def extract_date_from_url(self, url):
        """Extract date information from archive URL patterns."""
        # Common patterns in TV news archives:
        # /2024/01/ or /2024-01/ or /january-2024/
        patterns = [
            r'/(\d{4})/(\d{1,2})/?',  # /2024/1/ or /2024/01/
            r'/(\d{4})-(\d{1,2})/?',  # /2024-01/
            r'/(\w+)-(\d{4})/?',      # /january-2024/
            r'/(\d{4})(\d{2})/?',     # /202401/
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                try:
                    groups = match.groups()
                    if len(groups) == 2:
                        if groups[0].isdigit() and groups[1].isdigit():
                            # Year-month pattern
                            year, month = int(groups[0]), int(groups[1])
                            return date(year, month, 1)
                        elif groups[1].isdigit():
                            # Month-year pattern
                            month_name, year = groups[0], int(groups[1])
                            month_num = self.parse_month_name(month_name)
                            if month_num:
                                return date(year, month_num, 1)
                except (ValueError, TypeError):
                    continue
                    
        # Fallback: try to extract any year from URL
        year_match = re.search(r'/(\d{4})/', url)
        if year_match:
            try:
                year = int(year_match.group(1))
                # Assume January if no month found
                return date(year, 1, 1)
            except ValueError:
                pass
                
        return None
        
    def parse_month_name(self, month_name):
        """Convert month name to number."""
        month_mapping = {
            'january': 1, 'jan': 1,
            'february': 2, 'feb': 2,
            'march': 3, 'mar': 3,
            'april': 4, 'apr': 4,
            'may': 5,
            'june': 6, 'jun': 6,
            'july': 7, 'jul': 7,
            'august': 8, 'aug': 8,
            'september': 9, 'sep': 9, 'sept': 9,
            'october': 10, 'oct': 10,
            'november': 11, 'nov': 11,
            'december': 12, 'dec': 12
        }
        return month_mapping.get(month_name.lower())
        
    def should_process_temporal_link(self, url):
        """Determine if URL should be processed based on temporal constraints."""
        link_date = self.extract_date_from_url(url)
        
        if not link_date:
            # If we can't parse the date, be conservative and process it
            self.logger.warning(f'Could not extract date from URL: {url}, processing anyway')
            return True
            
        # Check against end date boundary
        if link_date > self.end_date:
            self.logger.debug(f'Skipping future date {link_date} > {self.end_date}: {url}')
            return False
            
        # Check against start date boundary if specified
        if self.start_date and link_date < self.start_date:
            self.logger.debug(f'Skipping past date {link_date} < {self.start_date}: {url}')
            return False
            
        return True

    def save_gzip_file(self, response, filename):
        """Save response body as gzipped file with error handling."""
        try:
            fn = filename + '.gz'
            with gzip.open(fn, 'wb') as f:
                f.write(response.body)
            self.logger.info(f'Saved file: {fn}')
            return True
        except Exception as e:
            self.logger.error(f'Failed to save file {filename}: {e}')
            return False

    def safe_extract(self, selector, method='get', default=''):
        """Safely extract data from selector with fallback."""
        try:
            if method == 'get':
                result = selector.get()
            elif method == 'getall':
                result = selector.getall()
            else:
                result = selector.extract()
            return result if result is not None else default
        except Exception as e:
            self.logger.warning(f'Extraction failed: {e}')
            return default

    def parse(self, response):
        """Parse the main site index page."""
        if response.status != 200:
            self.logger.error(f'Failed to load main page: {response.status}')
            return
            
        # Save main page
        page = response.url.split("/")[-2] or 'index'
        filename = f'{self.BASE_DIR}/vandy-{page}.html'
        self.save_gzip_file(response, filename)
        
        # Extract broadcast index links
        month_links = response.xpath("//table[@class='broadcastindex']//td/a")
        
        if not month_links:
            self.logger.warning('No month links found on main page')
            return
            
        self.logger.info(f'Found {len(month_links)} month links')

        # Count links that will be processed (after filtering)
        links_to_process = []
        for href in month_links:
            try:
                link_url = href.attrib.get('href')
                if not link_url:
                    continue
                full_url = urljoin(response.url, link_url)
                if not self.should_process_temporal_link(full_url):
                    continue
                if self.filter:
                    month = link_url.split('/')[-1] if '/' in link_url else 'all'
                    if not re.match(self.filter, month):
                        continue
                links_to_process.append(href)
            except Exception:
                pass

        self.total_months = len(links_to_process)
        self.pbar_months = tqdm(total=self.total_months, desc="Months", unit="month", position=0)
        self.pbar_broadcasts = tqdm(total=0, desc="Broadcasts", unit="item", position=1)

        for href in links_to_process:
            yield response.follow(
                href,
                self.parse_month_index,
                meta={'filter': self.filter} if self.filter else {}
            )

        self.logger.info(f'Processing {self.total_months} month links after temporal filtering')

    def parse_month_index(self, response):
        """Parse monthly broadcast index pages."""
        self.logger.info(f'Processing month index: {response.url}')
        self.months_processed += 1
        if self.pbar_months:
            self.pbar_months.update(1)
        
        # Check if we've hit our item limit
        if self.max_items > 0 and self.items_scraped >= self.max_items:
            self.logger.info(f'Reached max items limit: {self.max_items}')
            raise CloseSpider('max_items_reached')
        
        # Process evening broadcasts
        evening_links = response.xpath("//li[@class='elist_segment']/a")
        self.logger.info(f'Found {len(evening_links)} evening broadcasts')

        # Process special broadcasts
        special_links = response.xpath("//li[@class='slist_segment']/a")
        self.logger.info(f'Found {len(special_links)} special broadcasts')

        # Update expected broadcasts count
        new_broadcasts = len(evening_links) + len(special_links)
        self.total_broadcasts_expected += new_broadcasts
        if self.pbar_broadcasts:
            self.pbar_broadcasts.total = self.total_broadcasts_expected
            self.pbar_broadcasts.refresh()

        for href in evening_links:
            yield response.follow(
                href,
                self.parse_broadcast,
                meta={'list': 'evening'}
            )

        for href in special_links:
            yield response.follow(
                href,
                self.parse_broadcast,
                meta={'list': 'special'}
            )

    def parse_broadcast(self, response):
        """Parse individual broadcast pages."""
        self.logger.info(f'Processing broadcast: {response.url}')
        
        try:
            flist = response.meta.get('list', 'unknown')
            
            if flist == 'evening':
                # For evening broadcasts, follow to program page
                href = self.safe_extract(response.css('p.broadcast-info a::attr(href)'))
                if href:
                    yield response.follow(href, self.parse_program)
                else:
                    self.logger.warning(f'No program link found for evening broadcast: {response.url}')
            else:
                # For special broadcasts, extract data directly
                yield from self._extract_special_broadcast_data(response)
                
        except Exception as e:
            self.logger.error(f'Error parsing broadcast {response.url}: {e}')

    def _extract_special_broadcast_data(self, response):
        """Extract data from special broadcast pages."""
        try:
            idx = self._extract_id_from_url(response.url)
            if idx is None:
                return
                
            item = {}
            
            # Extract broadcast info
            broadcast_info = self.safe_extract(response.css('p.broadcast-info::text'))
            if broadcast_info and ' for ' in broadcast_info:
                parts = broadcast_info.split(' for ')
                item['program_title'] = parts[0].strip()
                item['date'] = parts[-1].strip()
            else:
                item['program_title'] = ''
                item['date'] = ''
                
            item['program_duration'] = ''
            item['broadcast_time'] = ''
            item['broadcast_title'] = self.safe_extract(response.css('h4.video-title::text')).strip()
            
            # Extract description
            description_texts = self.safe_extract(
                response.css('div.video-description *::text'), 
                method='getall', 
                default=[]
            )
            item['broadcast_abstract'] = ''.join([text.strip() for text in description_texts])
            item['broadcast_order'] = idx
            
            # Extract duration and reporters from metadata
            duration = self.safe_extract(
                response.xpath("//dl[@class='video-meta']/dt[.='Duration:']/following-sibling::dd/text()")
            )
            item['broadcast_duration'] = duration
            
            reporters = self.safe_extract(
                response.xpath("//dl[@class='video-meta']/dt[.='Reporters:']/following-sibling::dd/text()"),
                method='getall',
                default=[]
            )
            item['broadcast_reporter(s)'] = ''.join([r for r in reporters if r != duration])
            
            # Save HTML file
            filename = f'{self.BROADCASTS_DIR}/{idx}.html'
            self.save_gzip_file(response, filename)

            self.items_scraped += 1
            self.broadcasts_processed += 1
            if self.pbar_broadcasts:
                self.pbar_broadcasts.update(1)
            yield item

        except Exception as e:
            self.logger.error(f'Error extracting special broadcast data: {e}')

    def parse_broadcast_evening(self, response):
        """Parse evening broadcast pages."""
        self.logger.info(f'Processing evening broadcast: {response.url}')
        
        try:
            item = response.meta.get('program_data', {}).copy()
            idx = self._extract_id_from_url(response.url)
            
            if idx is None:
                return
                
            # Extract broadcast-specific data
            broadcast_info = self.safe_extract(response.css('p.broadcast-info::text'))
            if broadcast_info and ' for ' in broadcast_info:
                item['date'] = broadcast_info.split(' for ')[-1].strip()
            
            item['broadcast_title'] = self.safe_extract(response.css('h4.video-title::text')).strip()
            
            # Extract description
            description_texts = self.safe_extract(
                response.css('div.video-description *::text'),
                method='getall',
                default=[]
            )
            item['broadcast_abstract'] = ''.join([text.strip() for text in description_texts])
            item['broadcast_order'] = idx
            
            # Try multiple XPath expressions for duration (handle format variations)
            duration = (
                self.safe_extract(response.xpath("//dl[@class='video-meta']/dt[.='Duration:']/following-sibling::dd/text()")) or
                self.safe_extract(response.xpath("//dt[.='Duration:']/following-sibling::dd/text()"))
            )
            item['broadcast_duration'] = duration
            
            # Extract reporters
            reporters = self.safe_extract(
                response.xpath("//dl[@class='video-meta']/dt[.='Reporter(s):']/following-sibling::dd/text()"),
                method='getall',
                default=[]
            )
            item['broadcast_reporter(s)'] = ''.join([r for r in reporters if r != duration])
            
            # Save HTML file
            filename = f'{self.BROADCASTS_DIR}/{idx}.html'
            self.save_gzip_file(response, filename)

            self.items_scraped += 1
            self.broadcasts_processed += 1
            if self.pbar_broadcasts:
                self.pbar_broadcasts.update(1)
            yield item

        except Exception as e:
            self.logger.error(f'Error parsing evening broadcast {response.url}: {e}')

    def parse_program(self, response):
        """Parse program pages and extract broadcast listings."""
        self.logger.info(f'Processing program: {response.url}')
        
        try:
            idx = self._extract_id_from_url(response.url)
            if idx is None:
                return
                
            filename = f'{self.PROGRAMS_DIR}/{idx}.html'
            self.save_gzip_file(response, filename)
            
            # Extract program metadata
            title = self.safe_extract(response.css('h4.program-headline::text'))
            if title:
                title = title.strip().split(' for ')[0]
                
            duration_text = self.safe_extract(response.css('p.program-duration::text'))
            duration = self._extract_duration(duration_text)
            
            # Extract broadcast listings
            ids = self.safe_extract(response.css('li.listing p.id em::text'), method='getall', default=[])
            timestamps = self.safe_extract(response.css('li.listing p.timestamp::text'), method='getall', default=[])
            hrefs = self.safe_extract(response.css('li.listing a::attr(href)'), method='getall', default=[])
            
            # Process each broadcast in the program
            for broadcast_id, ts, href in zip(ids, timestamps, hrefs):
                if ts:
                    ts = ts.strip().replace(' — ', '-')
                    
                meta = {
                    'program_data': {
                        'program_title': title,
                        'program_duration': duration,
                        'broadcast_time': ts
                    }
                }
                yield response.follow(
                    href, 
                    self.parse_broadcast_evening, 
                    meta=meta, 
                    dont_filter=True
                )
                
        except Exception as e:
            self.logger.error(f'Error parsing program {response.url}: {e}')

    def _extract_id_from_url(self, url):
        """Extract numeric ID from URL."""
        try:
            return int(url.split('/')[-1])
        except (ValueError, IndexError):
            self.logger.warning(f'Could not extract ID from URL: {url}')
            return None

    def _extract_duration(self, duration_text):
        """Extract duration from text using regex."""
        if not duration_text:
            return ''
            
        match = re.search(r'This program is\s(.*?)\slong', duration_text)
        return match.group(1) if match else duration_text.strip()

    def closed(self, reason):
        """Called when spider closes."""
        if self.pbar_months:
            self.pbar_months.close()
        if self.pbar_broadcasts:
            self.pbar_broadcasts.close()
        self.logger.info(f'Spider closed: {reason}. Total items scraped: {self.items_scraped}')
        self.logger.info(f'Months processed: {self.months_processed}/{self.total_months}')
        self.logger.info(f'Broadcasts processed: {self.broadcasts_processed}')
        self.logger.info(f'Temporal range: {self.start_date or "beginning"} to {self.end_date}')