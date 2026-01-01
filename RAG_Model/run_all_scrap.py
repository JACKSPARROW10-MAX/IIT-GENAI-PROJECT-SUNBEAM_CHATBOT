import sys
import os
import time

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)


def run_full_scraper():
    """
    Re-scrapes all data sources and rebuilds the vector database
    """

    from Data_Scraping.Course_scrap import scrape_courses
    from Data_Scraping.Intership_sc import scrape_internships
    from Data_Scraping.About_us_sc import main
    from Data_Scraping.PreCAT_sc import scrape_precat_course

    from Loaders.MyLoader import MyLoader
    from Chroma_DB.data_to_chroma import rebuild_chroma_db

    print("🔄 Starting full data re-scraping...")

    # 1. Run all scrapers
    course_data = scrape_courses()
    internship_data = scrape_internships()
    about_data = main()
    pre_cat_data = scrape_precat_course()

    # 2. Combine all scraped data
    all_documents = []
    all_documents.extend(course_data)
    all_documents.extend(internship_data)
    all_documents.extend(about_data)
    all_documents.extend(pre_cat_data)

    # 3. Load documents using custom loader
    loader = MyLoader(all_documents)
    docs = loader.lazyload()

    # 4. Rebuild ChromaDB (delete + reinsert embeddings)
    rebuild_chroma_db()
    print("✅ Full data re-scraping and DB update completed")
