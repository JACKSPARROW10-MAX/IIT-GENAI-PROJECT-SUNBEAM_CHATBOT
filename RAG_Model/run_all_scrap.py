import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)


def run_full_scraper():
    """
    Re-scrapes all data sources and rebuilds the Chroma vector database.
    """

    from Data_Scraping.driver_factory import create_driver

    from Data_Scraping.About_us_sc import scrape_about
    from Data_Scraping.Course_scrap import scrape_all_courses
    from Data_Scraping.Intership_sc import scrape_all_internships
    from Data_Scraping.PreCAT_sc import scrape_precat_courses

    from Loaders.MyLoader import MyLoader
    from Chroma_DB.data_to_chroma import rebuild_chroma_db

    print("🔄 Starting full data re-scraping pipeline...")

    driver = create_driver()

    try:
        about_data = scrape_about(driver)
        course_data = scrape_all_courses(driver)
        internship_data = scrape_all_internships(driver)
        precat_data = scrape_precat_courses(driver)

    finally:
        driver.quit()

    all_documents = []
    all_documents.extend(about_data)
    all_documents.extend(course_data)
    all_documents.extend(internship_data)
    all_documents.extend(precat_data)

    print(f"📄 Total documents collected: {len(all_documents)}")

    loader = MyLoader(all_documents)
    docs = loader.lazyload()

    rebuild_chroma_db(docs)

    print("✅ Full data re-scraping and Chroma DB update completed")


if __name__ == "__main__":
    run_full_scraper()
