import requests
import time
import json
import os
import pandas as pd
import streamlit as st
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from urllib.parse import urlparse

def parse_linkedin(soup):
    """Extract job postings from LinkedIn job board."""
    job_listings = soup.find_all('div', {'class': 'job-search-card'})
    jobs = []
    
    for job in job_listings:
        try:
            title = job.find('h3', {'class': 'base-search-card__title'}).text.strip()
            company = job.find('h4', {'class': 'base-search-card__subtitle'}).text.strip()
            date_posted = job.find('time')['datetime']
            job_link = job.find('a', {'class': 'base-card__full-link'})['href']
            
            jobs.append({
                'Title': title,
                'Company': company,
                'Date Posted': date_posted[:10],
                'Job Link': job_link
            })
        except (AttributeError, KeyError):
            continue  # Skip if parsing fails for a specific job
        
    return jobs

def parse_indeed(soup):
    """Extract job postings from Indeed job board."""
    job_listings = soup.find_all('div', {'class': 'job_seen_beacon'})
    jobs = []
    
    for job in job_listings:
        try:
            title = job.find('h2', {'class': 'jobTitle'}).text.strip()
            company = job.find('span', {'class': 'companyName'}).text.strip()
            date_posted = job.find('span', {'class': 'date'}).text.strip()
            job_link = 'https://www.indeed.com' + job.find('a', {'class': 'jcs-JobTitle'})['href']
            
            jobs.append({
                'Title': title,
                'Company': company,
                'Date Posted': date_posted,
                'Job Link': job_link
            })
        except (AttributeError, KeyError):
            continue  
    
    return jobs

def parse_glassdoor(soup):
    """Extract job postings from Glassdoor job board."""
    job_listings = soup.find_all('li', {'class': 'react-job-listing'})
    jobs = []
    
    for job in job_listings:
        try:
            title = job.find('a', {'class': 'jobLink'}).text.strip()
            company = job.find('div', {'class': 'job-search-key-l2wjgv e1n63ojh0'}).text.strip()
            date_posted = job.find('div', {'class': 'd-flex align-items-end pl-std css-17n8uzw'}).text.strip()
            job_link = 'https://www.glassdoor.com' + job.find('a', {'class': 'jobLink'})['href']
            
            jobs.append({
                'Title': title,
                'Company': company,
                'Date Posted': date_posted,
                'Job Link': job_link
            })
        except (AttributeError, KeyError):
            continue  
    
    return jobs

def parse_generic(soup):
    """Fallback method to extract job postings from an unknown job board."""
    jobs = []
    
    job_listings = soup.find_all('a', href=True)
    
    for job in job_listings:
        try:
            title = job.text.strip()
            job_link = job['href']
            
            if "job" in job_link.lower() or "career" in job_link.lower():
                jobs.append({
                    'Title': title if title else "Unknown",
                    'Company': "Unknown",
                    'Date Posted': "Unknown",
                    'Job Link': job_link
                })
        except (AttributeError, KeyError):
            continue  

    return jobs

def get_job_postings(company_urls, days_back=14):
    """Fetch job postings from various job board URLs dynamically."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    all_jobs = []
    cutoff_date = datetime.now() - timedelta(days=days_back)
    
    # Mapping job boards to their specific parsers
    parsers = {
        'linkedin.com': parse_linkedin,
        'indeed.com': parse_indeed,
        'glassdoor.com': parse_glassdoor
    }
    
    for url in company_urls:
        with st.spinner(f'Scraping jobs from {url}...'):
            try:
                response = requests.get(url, headers=headers)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                domain = urlparse(url).netloc.replace('www.', '')
                parser = parsers.get(domain, parse_generic)  # Choose the right parser
                
                jobs = parser(soup)  # Extract job postings
                
                for job in jobs:
                    if job['Date Posted'] != "Unknown":
                        try:
                            post_date = datetime.strptime(job['Date Posted'], '%Y-%m-%d')
                            if post_date < cutoff_date:
                                continue
                        except ValueError:
                            pass  # Ignore invalid date formats
                    
                    all_jobs.append(job)
                
                time.sleep(3)  # Avoid getting blocked
                
            except Exception as e:
                st.error(f"Error scraping {url}: {str(e)}")
                continue
    
    return pd.DataFrame(all_jobs) if all_jobs else pd.DataFrame()

def load_saved_lists():
    """Load saved job board URLs."""
    if os.path.exists('saved_url_lists.json'):
        with open('saved_url_lists.json', 'r') as f:
            return json.load(f)
    return {}

def save_url_lists(lists):
    """Save job board URLs."""
    with open('saved_url_lists.json', 'w') as f:
        json.dump(lists, f)

def delete_saved_list(list_name):
    """Delete a saved job board URL list."""
    if os.path.exists('saved_url_lists.json'):
        with open('saved_url_lists.json', 'r') as f:
            saved_lists = json.load(f)
        if list_name in saved_lists:
            del saved_lists[list_name]
            with open('saved_url_lists.json', 'w') as f:
                json.dump(saved_lists, f)
            return True
    return False
