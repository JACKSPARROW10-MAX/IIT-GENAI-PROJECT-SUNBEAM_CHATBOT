import logging
from typing import Iterator, List, Dict, Any, Union
from langchain_core.document_loaders.base import BaseLoader
from langchain_core.documents import Document

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SunbeamDataLoader(BaseLoader):
    """
    Specialized loader for Sunbeam Institute scraped data.
    Handles nested dictionaries and lists commonly returned by scrapers.
    """

    def __init__(self, data: Union[Dict[str, Any], List[Dict[str, Any]]], source: str = "Scraped Data"):
        """
        :param data: The scraped data (either a single dict or a list of dicts).
        :param source: A label for the source (e.g., 'About Us' or 'Course Page').
        """
        self.data = data
        self.source = source

    def lazy_load(self) -> Iterator[Document]:
        """Convert the input data into LangChain Document objects."""
        if isinstance(self.data, list):
            for idx, item in enumerate(self.data):
                yield self._process_item(item, f"{self.source} - Item {idx+1}")
        elif isinstance(self.data, dict):
            yield self._process_item(self.data, self.source)
        else:
            logger.error(f"Invalid data format passed to SunbeamDataLoader: {type(self.data)}")

    def _process_item(self, item: Dict[str, Any], source_label: str) -> Document:
        """Helper to convert a dictionary item into a Document."""
        # Extract title if available
        title = (
            item.get("Course Title") 
            or item.get("title") 
            or item.get("Title") 
            or source_label
        )
        
        # Flatten dictionary to text
        content = self._flatten_dict_to_text(item)
        
        return Document(
            page_content=content,
            metadata={
                "source": source_label,
                "title": title,
                "type": "scraped_content"
            }
        )

    def _flatten_dict_to_text(self, data: Dict[str, Any], indent: int = 0) -> str:
        """Recursively converts nested dictionaries and lists to a readable string."""
        lines = []
        prefix = "  " * indent
        
        for key, value in data.items():
            if not value:
                continue
                
            if isinstance(value, dict):
                lines.append(f"{prefix}### {key}:")
                lines.append(self._flatten_dict_to_text(value, indent + 1))
            elif isinstance(value, list):
                lines.append(f"{prefix}**{key}**:")
                for sub_item in value:
                    if isinstance(sub_item, dict):
                        lines.append(self._flatten_dict_to_text(sub_item, indent + 1))
                    else:
                        lines.append(f"{prefix}  • {sub_item}")
            else:
                lines.append(f"{prefix}**{key}**: {value}")
                
        return "\n".join(lines)

    def load(self) -> List[Document]:
        """Eagerly load all documents."""
        return list(self.lazy_load())
