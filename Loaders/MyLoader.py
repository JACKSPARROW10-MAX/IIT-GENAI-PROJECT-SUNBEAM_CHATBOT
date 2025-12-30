from langchain_community.document_loaders.base import BaseLoader
from langchain_core.documents import Document
from typing import Iterator, Callable, Union, Any


class MyLoader(BaseLoader):
    """
    Custom Loader for Sunbeam Website Scraped Data

    Converts scraped Python data (dict / list)
    into LangChain Document objects.
    """

    def __init__(self, scraper_func: Callable[[], Union[dict, list]], source_name: str):
        """
        :param scraper_func: function with NO arguments (use lambda if needed)
        :param source_name: source identifier (PDF path or page name)
        """
        self.scraper_func = scraper_func
        self.source_name = source_name

    def lazy_load(self) -> Iterator[Document]:
        """
        Required by LangChain BaseLoader
        Yields Document objects
        """
        scraped_data = self.scraper_func()

        # Case 1: (Courses, Internships)
        if isinstance(scraped_data, list):
            for item in scraped_data:
                yield Document(
                    page_content=self._dict_to_text(item),
                    metadata={
                        "source": self.source_name,
                        "title": (
                            item.get("Course Title")
                            or item.get("Title")
                            or "Sunbeam Course"
                        )
                    }
                )

        # Case 2:(About Us, Pre-CAT)
        elif isinstance(scraped_data, dict):
            yield Document(
                page_content=self._dict_to_text(scraped_data),
                metadata={
                    "source": self.source_name,
                    "title": "Sunbeam Info"
                }
            )

    
    def _dict_to_text(self, data: dict) -> str:
        """
        Converts nested dict/list data into LLM-readable text
        """
        lines = []

        for key, value in data.items():
            if isinstance(value, list):
                lines.append(f"{key}:")
                for item in value:
                    lines.append(f"- {item}")

            elif isinstance(value, dict):
                lines.append(f"{key}:")
                for k, v in value.items():
                    lines.append(f"- {k}: {v}")

            else:
                lines.append(f"{key}: {value}")

        return "\n".join(lines)



if __name__ == "__main__":
    from Data_Scraping.Course_scrap import scrape_course_data

    course_urls = "https://sunbeaminfo.in/modular-courses/data-structure-algorithms-using-java"

    # FIXED: Use lambda to create a no-arg function
    course_loader = MyLoader(
        scraper_func=lambda: scrape_course_data(course_urls),
        source_name=r"D:\Sunbeam\IIT-GENAI-PROJECT-SUNBEAM_CHATBOT\Data\Course_data.pdf"
    )

    docs = list(course_loader.lazy_load())  # Convert to list to iterate
    for document in docs:
        print(document)
        print("-" * 50)
