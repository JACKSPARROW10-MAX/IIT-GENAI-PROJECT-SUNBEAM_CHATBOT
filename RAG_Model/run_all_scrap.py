import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)


def run_full_scraper():
    """
    Re-scrapes all data sources and rebuilds the Chroma vector database.
    """

    from Data_Scraping.driver_factory import create_driver

    from Data_Scraping.About_us_sc import main as scrape_about
    from Data_Scraping.Course_scrap import main as scrape_courses
    from Data_Scraping.Intership_sc import scrape_internships
    from Data_Scraping.PreCAT_sc import scrape_precat_course

    from Chroma_DB.data_to_chroma import upsert_documents

    print("🔄 Starting full data re-scraping pipeline...")

    # Run scrapers that create their own drivers
    print("📄 Scraping About Us data...")
    scrape_about()
    
    print("📄 Scraping Course data...")
    scrape_courses()
    
    # Run scrapers that need a shared driver
    driver = create_driver()
    try:
        print("📄 Scraping Internship data...")
        scrape_internships(driver)
        
        print("📄 Scraping PreCAT data...")
        scrape_precat_course(driver)
    finally:
        driver.quit()

    # Upload all PDFs to Chroma
    print("📤 Uploading data to Chroma...")
    upsert_documents()

    print("✅ Full data re-scraping and Chroma DB update completed")


if __name__ == "__main__":
    run_full_scraper()
