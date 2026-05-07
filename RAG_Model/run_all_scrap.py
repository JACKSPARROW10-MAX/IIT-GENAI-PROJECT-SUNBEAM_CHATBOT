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
    Individual scraper failures are logged but do NOT stop the pipeline.
    """
    from Data_Scraping import driver_factory
    from Data_Scraping.About_us_sc import scrape_about
    from Data_Scraping.Course_scrap import scrape_all_courses
    from Data_Scraping.Intership_sc import scrape_all_internships
    from Data_Scraping.PreCAT_sc import scrape_precat_courses
    from Chroma_DB.data_to_chroma import upsert_documents

    logger.info("🔄 Starting full data re-scraping pipeline...")
    
    success_count = 0
    fail_count = 0

    # 1. Scrape About Us
    try:
        logger.info("📄 [1/4] Scraping About Us data...")
        scrape_about()
        success_count += 1
        logger.info("✅ About Us scraping completed.")
    except Exception as e:
        fail_count += 1
        logger.error(f"❌ About Us scraping failed: {str(e)}")

    # 2. Scrape Courses
    try:
        logger.info("📄 [2/4] Scraping Course data...")
        scrape_all_courses()
        success_count += 1
        logger.info("✅ Course scraping completed.")
    except Exception as e:
        fail_count += 1
        logger.error(f"❌ Course scraping failed: {str(e)}")

    # 3. Scrape Internship (shared driver)
    driver = driver_factory.create_driver()
    try:
        try:
            logger.info("📄 [3/4] Scraping Internship data...")
            scrape_all_internships(driver)
            success_count += 1
            logger.info("✅ Internship scraping completed.")
        except Exception as e:
            fail_count += 1
            logger.error(f"❌ Internship scraping failed: {str(e)}")

        # 4. Scrape PreCAT (reuse driver)
        try:
            logger.info("📄 [4/4] Scraping PreCAT data...")
            scrape_precat_courses(driver)
            success_count += 1
            logger.info("✅ PreCAT scraping completed.")
        except Exception as e:
            fail_count += 1
            logger.error(f"❌ PreCAT scraping failed: {str(e)}")
    finally:
        driver.quit()

    # 5. Ingest whatever was scraped into Chroma
    logger.info(f"📊 Scraping summary: {success_count} succeeded, {fail_count} failed")
    
    if success_count == 0:
        logger.error("❌ All scrapers failed. Skipping Chroma upload.")
        return

    logger.info("📤 Uploading scraped PDFs to ChromaDB...")
    try:
        upsert_documents()
        logger.info("✅ Chroma DB update completed.")
    except Exception as e:
        logger.error(f"❌ Chroma upload failed: {str(e)}")

    logger.info(f"🏁 Pipeline finished. {success_count}/4 scrapers succeeded.")

if __name__ == "__main__":
    run_full_scraper()
