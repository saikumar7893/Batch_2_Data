import os
import time
from datetime import date
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd

class BeaconHillJobScraper:
    def __init__(self):
        self.npo_jobs = {}
        self.job_no = 0
        self.company_name = "Beacon Hill"
        self.contact = "617.326.4000"
        self.Work_type = "NA"
        self.current_date = date.today().strftime("%Y-%m-%d")
        self.keywords = ["Data Analyst", "Business Analyst", "System Analyst", "Data Scientists", "Data engineer", "Business System Analyst"]

    def create_output_folder(self):
        output_folder = os.path.join(os.getcwd(), 'output')
        os.makedirs(output_folder, exist_ok=True)
        return output_folder

    def create_subfolder_with_date(self, output_folder):
        subfolder_path = os.path.join(output_folder, self.current_date)
        os.makedirs(subfolder_path, exist_ok=True)
        return subfolder_path

    def create_csv_file(self, subfolder_path):
        file_name = 'job_portal.csv'
        csv_path = os.path.join(subfolder_path, file_name)
        return csv_path

    def scrape_jobs(self):
        output_folder = self.create_output_folder()
        subfolder_path = self.create_subfolder_with_date(output_folder)
        csv_path = self.create_csv_file(subfolder_path)

        existing_job_urls = set()

        if os.path.exists(csv_path):
            existing_data = pd.read_csv(csv_path)
            existing_job_urls = set(existing_data['Job Posting Url'])

        for value in self.keywords:
            print(f"Scraping data for the job role: {value}...")
            chrome_options = Options()
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--headless')
            driver = webdriver.Chrome(options=chrome_options)
            driver.get("https://jobs.beaconhillstaffing.com/job-search/")
            driver.maximize_window()

            driver.find_element(By.XPATH, '//*[@id="CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"]').click()
            time.sleep(5)
            driver.find_element(By.XPATH, '//*[@data-value="ea862cbfd4ee5a8cff48853fe0fdd701"]').click()
            time.sleep(5)
            driver.find_element(By.XPATH, '//*[@placeholder="Keyword or Job Title"]').send_keys(value)
            time.sleep(5)
            jobs = driver.find_elements(By.XPATH, '//*[@class="row parv_row_parent"]')

            for job in jobs:
                joburl = job.find_element(By.TAG_NAME, 'a').get_attribute('href')

                if joburl in existing_job_urls:
                    continue

                job_name = job.find_element(By.TAG_NAME, 'h3').text

                if all(keyword.lower() in job_name.lower() for keyword in value.split()):
                    self.job_no += 1
                    job_location = job.find_element(By.XPATH, './/*[@class="col-md-3 location"]//p').text
                    job_type = job.find_element(By.XPATH, './/*[@class="col-md-3 job_Type type_col"]//p').text
                    job_pay = job.find_element(By.XPATH, './/*[@class="col-md-3 pay_rate pay_col"]//p').text
                    job_post_date = job.find_element(By.XPATH, './/*[@class="posted_date_job_search_custom"]').text

                    list1 = [self.company_name, self.current_date, job_name, job_type, job_pay, joburl, job_location,
                             job_post_date, self.contact, self.Work_type]
                    self.npo_jobs[self.job_no] = list1
            # Close the browser after scraping data for each keyword
            driver.quit()

        # Append or create CSV file
        npo_jobs_df = pd.DataFrame.from_dict(self.npo_jobs, orient='index',
                                             columns=['Vendor Company Name', 'Date & Time Stamp', 'Job Title',
                                                      'Job Type', 'Pay Rate', 'Job Posting Url', 'Job Location',
                                                      'Job Posting Date', 'Contact Person', 'Work Type (Remote /Hybrid /Onsite)'])

        print(npo_jobs_df.head(self.job_no))

        if os.path.exists(csv_path):
            existing_data = pd.read_csv(csv_path)
            updated_data = pd.concat([existing_data, npo_jobs_df], ignore_index=True)
            updated_data.to_csv(csv_path, index=False)
            print(f"Appended data to existing CSV: {csv_path}")
        else:
            npo_jobs_df.to_csv(csv_path, index=False)
            print(f"Created new CSV: {csv_path}")

# Example usage:
# if __name__ == "__main__":
#     beacon_hill_scraper = BeaconHillJobScraper()
#     beacon_hill_scraper.scrape_jobs()
