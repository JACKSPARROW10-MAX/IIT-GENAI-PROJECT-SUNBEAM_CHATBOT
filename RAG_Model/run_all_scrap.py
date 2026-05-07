import os
import sys
import logging

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_full_scraper():
    """
    Re-scrapes all data sources and rebuilds the Chroma vector database.
    """
    from Data_Scraping import driver_factory
    from Data_Scraping.About_us_sc import scrape_about
    from Data_Scraping.Course_scrap import scrape_all_courses
    from Data_Scraping.Intership_sc import scrape_all_internships
    from Data_Scraping.PreCAT_sc import scrape_precat_courses
    from Chroma_DB.data_to_chroma import upsert_documents

    logger.info("🔄 Starting full data re-scraping pipeline...")

    # 1. Scrape About Us
    logger.info("📄 Scraping About Us data...")
    scrape_about()
    
    # 2. Scrape Courses
    logger.info("📄 Scraping Course data...")
    scrape_all_courses()
    
    # 3. Scrape Internship and PreCAT (using shared driver)
    driver = driver_factory.create_driver()
    try:
        logger.info("📄 Scraping Internship data...")
        scrape_all_internships(driver)
        
        logger.info("📄 Scraping PreCAT data...")
        scrape_precat_courses(driver)
    finally:
        driver.quit()

    # 4. Ingest into Chroma
    logger.info("📤 Uploading scraped PDFs to ChromaDB...")
    upsert_documents()

    logger.info("✅ Full data re-scraping and Chroma DB update completed successfully.")

if __name__ == "__main__":
    run_full_scraper()
