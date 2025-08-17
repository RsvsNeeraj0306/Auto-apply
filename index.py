from time import sleep
import json
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from datetime import datetime

from driver import Driver as driver
from filter_jobs import filter_recent_jobs  # Add this import

# Add your blacklist here
SKIP_COMPANIES = [
    "Accenture",
    "TCS",
    "Infosys"
    # Add more company names as needed
]

apply_button_xpath = "//*[(@id='apply-button')]"
company_site_button_xpath = "//*[(@id = 'company-site-button')]"
save_button_xpath = "//*[(@class = 'styles_save-job-button__WLm_s')]"

# List to store job application results
job_results = []

print(f"Starting job application process...")

# Filter jobs to only recent ones (within 2 weeks)
print("Filtering jobs by posting date...")
filter_recent_jobs(
    input_file="./data/jobs.jsonl",
    output_file="./data/recent_jobs.jsonl",
    max_days=14  # Only jobs posted within 2 weeks
)

# Use the filtered jobs file instead of the original
with open("./data/recent_jobs.jsonl", "r", encoding="utf-8") as f:
    lines = f.readlines()
    print(f"Found {len(lines)} recent jobs to process")
    
    for i, line in enumerate(lines):
        print(f"\nProcessing job {i+1}/{len(lines)}")
        job = json.loads(line)
        link = job.get("link", "")
        job_title = job.get("title", "Unknown")
        company = job.get("company", "Unknown")
        posted = job.get("posted", "Unknown")
        
        # Skip blacklisted companies
        if company in SKIP_COMPANIES:
            print(f"Skipping job at blacklisted company: {company}")
            job_result = {
                "job_title": job_title,
                "company": company,
                "link": link,
                "posted": posted,
                "applied": False,
                "saved": False,
                "status": "Skipped",
                "reason": "Company is blacklisted",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            job_results.append(job_result)
            continue
        
        print(f"Job: {job_title} at {company}")
        print(f"Posted: {posted}")
        print(f"Link: {link}")
        
        # Initialize job result
        job_result = {
            "job_title": job_title,
            "company": company,
            "link": link,
            "posted": posted,  # Add posted date to result
            "applied": False,
            "saved": False,
            "status": "Not processed",
            "reason": "",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        isApplyFound = True
        if link:
            driver.get(link)
            
            # Add 30 second login time for first job
            if i == 0:
                print("You have 30 seconds to log in to Naukri...")
                sleep(30)
            
            sleep(5)
            try:
                apply_button = driver.find_element(By.XPATH, apply_button_xpath)
                if apply_button:
                    apply_button.click()
                    sleep(5)
                    try:
                        element = driver.find_element(By.CLASS_NAME, "_chatBotContainer")
                        print("Element with class '_chatBotContainer' is present.")
                        help = input("Enter `P` to proceed with the application, or any other key to skip: ")
                        if help.lower() == 'p':
                            print("Proceeding with the application.")
                            job_result["applied"] = True
                            job_result["status"] = "Applied"
                            job_result["reason"] = "Successfully applied"
                        else: 
                            save_button = driver.find_element(By.XPATH, save_button_xpath)
                            if save_button:
                                save_button.click()
                                job_result["saved"] = True
                                job_result["status"] = "Saved"
                                job_result["reason"] = "User chose to save instead of apply"
                            continue
                    except NoSuchElementException:
                        print("Element with class '_chatBotContainer' is not present.")
                        job_result["applied"] = True
                        job_result["status"] = "Applied"
                        job_result["reason"] = "Applied successfully (no chatbot)"
                        
            except NoSuchElementException as e:
                isApplyFound = False
                print(f"Apply button was not found")
                
            if not isApplyFound:            
                try:
                    save_button = driver.find_element(By.XPATH, save_button_xpath)
                    if save_button:
                        save_button.click()
                        job_result["saved"] = True
                        job_result["status"] = "Saved"
                        job_result["reason"] = "Apply button not found, job saved instead"
                except NoSuchElementException as e:
                    print(f"Save button not found")
                    print("No apply button found, skipping to next job.")
                    job_result["status"] = "Failed"
                    job_result["reason"] = "Neither apply nor save button found"
                    continue
            sleep(5)
        else:
            job_result["status"] = "Failed"
            job_result["reason"] = "No job link provided"
        
        # Add job result to list
        job_results.append(job_result)
        
        # Save results after each job
        with open("./data/job_application_results.jsonl", "w", encoding="utf-8") as result_file:
            for result in job_results:
                json.dump(result, result_file, ensure_ascii=False)
                result_file.write("\n")

# Final summary
print(f"\n=== JOB APPLICATION SUMMARY ===")
applied_jobs = [job for job in job_results if job["applied"]]
saved_jobs = [job for job in job_results if job["saved"]]
failed_jobs = [job for job in job_results if job["status"] == "Failed"]
skipped_jobs = [job for job in job_results if job["status"] == "Skipped"]

print(f"Total recent jobs processed: {len(job_results)}")
print(f"Successfully applied: {len(applied_jobs)}")
print(f"Saved jobs: {len(saved_jobs)}")
print(f"Failed jobs: {len(failed_jobs)}")
print(f"Skipped jobs (blacklisted companies): {len(skipped_jobs)}")

# Save final summary
summary = {
    "total_processed": len(job_results),
    "applied_count": len(applied_jobs),
    "saved_count": len(saved_jobs),
    "failed_count": len(failed_jobs),
    "skipped_count": len(skipped_jobs),
    "applied_jobs": [{"title": job["job_title"], "company": job["company"], "posted": job.get("posted")} for job in applied_jobs],
    "saved_jobs": [{"title": job["job_title"], "company": job["company"], "posted": job.get("posted")} for job in saved_jobs],
    "failed_jobs": [{"title": job["job_title"], "company": job["company"], "reason": job["reason"], "posted": job.get("posted")} for job in failed_jobs],
    "skipped_jobs": [{"title": job["job_title"], "company": job["company"], "posted": job.get("posted")} for job in skipped_jobs],
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "blacklisted_companies": SKIP_COMPANIES
}

with open("./data/application_summary.json", "w", encoding="utf-8") as summary_file:
    json.dump(summary, summary_file, ensure_ascii=False, indent=2)

print(f"\nResults saved to:")
print(f"- Detailed log: ./data/job_application_results.jsonl")
print(f"- Summary: ./data/application_summary.json")