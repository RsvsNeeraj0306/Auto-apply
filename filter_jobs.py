from datetime import datetime, timedelta
import re
import json

def parse_posted_time(posted_str):
    """
    Parse the 'posted' field and return days ago as integer
    Examples: "1 week ago" -> 7, "3+ weeks ago" -> 21, "4 days ago" -> 4
    """
    if not posted_str:
        return float('inf')  # Very old if no data
    
    posted_str = posted_str.lower().strip()
    
    # Extract number and time unit
    if 'day' in posted_str:
        match = re.search(r'(\d+)', posted_str)
        if match:
            return int(match.group(1))
        return 1  # "yesterday" or similar
    
    elif 'week' in posted_str:
        match = re.search(r'(\d+)', posted_str)
        if match:
            weeks = int(match.group(1))
            if '3+' in posted_str or '+' in posted_str:
                weeks = max(weeks, 3)  # 3+ weeks = at least 3 weeks
            return weeks * 7
        return 7  # "1 week ago" or similar
    
    elif 'month' in posted_str:
        match = re.search(r'(\d+)', posted_str)
        if match:
            return int(match.group(1)) * 30
        return 30  # "1 month ago"
    
    else:
        return float('inf')  # Unknown format, treat as very old

def filter_recent_jobs(input_file, output_file, max_days=14):
    """
    Filter jobs posted within max_days (default 14 days = 2 weeks)
    """
    recent_jobs = []
    total_jobs = 0
    
    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            total_jobs += 1
            try:
                job = json.loads(line.strip())
                posted = job.get("posted", "")
                days_ago = parse_posted_time(posted)
                
                # Keep jobs posted within max_days
                if days_ago <= max_days:
                    recent_jobs.append(job)
                    print(f"✓ {job['title']} at {job['company']} - Posted: {posted} ({days_ago} days ago)")
                else:
                    print(f"✗ {job['title']} at {job['company']} - Posted: {posted} ({days_ago} days ago) - Too old")
                    
            except json.JSONDecodeError:
                continue
    
    # Save filtered jobs
    with open(output_file, "w", encoding="utf-8") as f:
        for job in recent_jobs:
            json.dump(job, f, ensure_ascii=False)
            f.write("\n")
    
    print(f"\n=== FILTERING SUMMARY ===")
    print(f"Total jobs: {total_jobs}")
    print(f"Recent jobs (≤ {max_days} days): {len(recent_jobs)}")
    print(f"Filtered jobs saved to: {output_file}")
    
    return recent_jobs

if __name__ == "__main__":
    # Filter jobs posted within last 2 weeks (14 days)
    filter_recent_jobs(
        input_file="./data/jobs.jsonl",
        output_file="./data/recent_jobs.jsonl",
        max_days=14
    )