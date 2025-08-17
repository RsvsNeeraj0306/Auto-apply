from bs4 import BeautifulSoup

def getJobData(html):
    soup = BeautifulSoup(html, 'html.parser')
    job_data = {}
    
    # Job Title
    job_data['title'] = soup.find('a', class_='title').get_text(strip=True)

    # Job Link
    job_data['link'] = soup.find('a', class_='title')['href']

    # Company Name
    job_data['company'] = soup.find('a', class_='comp-name').get_text(strip=True)

    # Company Rating
    rating_tag = soup.find('a', class_='rating')
    job_data['rating'] = rating_tag.find('span', class_='main-2').get_text(strip=True) if rating_tag else None

    # Experience
    exp_tag = soup.find('span', class_='expwdth')
    job_data['experience'] = exp_tag.get_text(strip=True) if exp_tag else None

    # Salary
    sal_tag = soup.find('span', class_='sal')
    job_data['salary'] = sal_tag.get_text(strip=True) if sal_tag else None

    # Location
    loc_tag = soup.find('span', class_='locWdth')
    job_data['location'] = loc_tag.get_text(strip=True) if loc_tag else None

    # Description
    desc_tag = soup.find('span', class_='job-desc')
    job_data['description'] = desc_tag.get_text(strip=True) if desc_tag else None

    # Skills/Tags
    tags = soup.find_all('li', class_='tag-li')
    job_data['skills'] = "#".join([tag.get_text(strip=True) for tag in tags])

    # Posted Date
    posted = soup.find('span', class_='job-post-day')
    job_data['posted'] = posted.get_text(strip=True) if posted else None

    # Job ID (from data attribute)
    wrapper = soup.find('div', class_='srp-jobtuple-wrapper')
    job_data['job_id'] = wrapper['data-job-id'] if wrapper else None

    return job_data