from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from util import getJobData
import json
import math
from string import Template
from driver import Driver as driver
import os
from datetime import datetime

seen_jobs = set()
count = 0
maxcount = 40

if os.path.exists("jobs.jsonl"):
    with open("jobs.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            try:
                job = json.loads(line)
                job_id = job.get("job_id")
                if job_id:
                    seen_jobs.add(job_id)
            except Exception:
                continue

# Add your blacklist here (wildcard: skip if any substring matches)
SKIP_COMPANIES = [
    "Accenture",
    "TCS",
    "Infosys"
    # Add more company names as needed
]

def is_blacklisted(company_name):
    """Return True if any blacklist name is found in the company_name (case-insensitive, partial match)."""
    company_name_lower = company_name.lower()
    for skip in SKIP_COMPANIES:
        if skip.lower() in company_name_lower:
            return True
    return False

def parsePage(soup) -> bool:
    global count
    if count >= maxcount:
        return False

    job_elems = soup.find_all('div', class_='srp-jobtuple-wrapper')
    with open("./data/jobs.jsonl", "a", encoding="utf-8") as f:
        for job_elem in job_elems:
            job_data = getJobData(str(job_elem))
            if job_data:
                job_id = job_data.get("job_id")
                company = job_data.get("company", "")
                # Skip blacklisted companies
                if is_blacklisted(company):
                    print(f"Skipping blacklisted company: {company}")
                    continue
                if job_id in seen_jobs:
                    continue
                seen_jobs.add(job_id)
                json.dump(job_data, f, ensure_ascii=False)
                f.write("\n")
                count += 1  
    return True

keywords = [ 'Quality Automation']

URL = Template(
    "https://www.naukri.com/$keyword-jobs-$p?experience=2&wfhType=0&wfhType=2&wfhType=3&glbl_qcrc=1019&glbl_qcrc=1028&ugTypeGid=12&cityTypeGid=17&cityTypeGid=97&cityTypeGid=134&cityTypeGid=139&cityTypeGid=183"
)

if __name__ == "__main__":
    try:
        urls = []
        for keyword in keywords:
            url = URL.substitute(keyword=keyword.lower().replace(' ', '-'), p=1)
            urls.append(url)
            driver.get(url)
            WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'styles_pages__v1rAK'))
            )
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            page_elem = soup.find('div', class_='styles_pages__v1rAK')
            count_elem = soup.find('span', class_='styles_count-string__DlPaZ')
            title_text = count_elem['title']  # "1 - 20 of 1014"
            total_jobs = int(title_text.split('of')[-1].strip())

            # Calculate total pages
            jobs_per_page = 20
            total_pages = math.ceil(total_jobs / jobs_per_page)
            print(f"total_jobs: {total_jobs}, total_pages: {total_pages}")
            if total_pages > 1:
                for i in range(2, total_pages + 1):
                    url = URL.substitute(keyword=keyword.lower().replace(' ', '-'), p=i)
                    urls.append(url)
                
        for url in urls:
            print(url)
            driver.get(url)
            WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'srp-jobtuple-wrapper'))
            )
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            success = parsePage(soup)
            if not success: 
                break

        print(f"Saved {count} new jobs to jobs.jsonl")

    except Exception as e:
        driver.quit()
        
    finally:
        print('Done')
        driver.quit()
