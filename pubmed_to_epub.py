import xml.etree.ElementTree as ET
from ebooklib import epub
import requests
import os

def create_epub_from_pubmed(pmcid:str = None, pmid:str = None, doi:str = None):
    '''
    This function creates an epub file from a PubMed Central article using E-utilities
    
    args:
        - pmcid:str
            PubMed Central ID (e.g., "PMC9953331")
    
    return:
        None
    '''
    # Count how many arguments are provided
    args_provded = sum(1 for arg in [pmcid, pmid, doi] if arg is not None)

    if args_provded != 1:
        raise ValueError("Provide only one ID (pmcid, pmid, or doi).")

    # 1. Fetch article data from E-utilities
    print("Fetching article from E-utilities...")
    
    # Base URL for E-utilities
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    search_url = f"{base_url}esearch.fcgi"

    # ---------------------------------
    # DOI => PMID => PMCID (Full-text)
    # ---------------------------------

    if doi:
        # Convert DOI to PMID
        print(f"DOI detected ({doi}). Converting to PMID...")

        search_params = {
            "db": "pubmed",
            "term": f"{doi}[doi]",
            "retmode": "json"
        }

        try:
            response = requests.get(search_url, params=search_params)
            response.raise_for_status()
            search_data = response.json()
            # Get idList array
            idlist = search_data.get("esearchresult", {}).get("idlist", [])

            if idlist:
                pmid = idlist[0]
                print(f"DOI {doi} converted to PMID {pmid}.")
            else:
                print("PMID not found for this DOI.")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error during request: {e}")
            return None

    # ---------------------------------
    # PMID => PMCID (Full-text)
    # ---------------------------------

    if pmid:
        if not pmid.isdigit():
            print(f"Invalid PMID detected ({pmid}). Try user other argument (pmcid, or doi).")
            return None

        # Convert PMID to PMCID
        print(f"PMID detected ({pmid}). Converting to PMCID...")

        search_params = {
            'dbfrom': 'pubmed',
            'db': 'pmc',
            'term': pmid,
            'retmode': 'json'
        }
    
        try:
            response = requests.get(search_url, params=search_params)
            response.raise_for_status()
            search_data = response.json()
            if not search_data['esearchresult']['idlist']:
                print(f"No article found for PMCID: PMC{pmid}")
                return None
            pmcid = article_id = search_data['esearchresult']['idlist'][0]
            print(f"PMID {pmid} converted to PMCID: {pmcid}")
        except requests.exceptions.RequestException as e:
            print(f"Error during request: {e}")
            return None

    return None
    # # Fetch full article data in XML format
    # fetch_url = f"{base_url}efetch.fcgi"
    # fetch_params = {
    #     'db': 'pmc',
    #     'id': article_id,
    #     'retmode': 'xml'
    # }
    
    # fetch_response = requests.get(fetch_url, params=fetch_params, timeout=30)
    # fetch_response.raise_for_status()
    
    # print(f"Successfully fetched article data")
    
    # # Parse XML content
    # try:
    #     root = ET.fromstring(fetch_response.content)
    # except ET.ParseError as e:
    #     print(f"Error parsing XML: {e}")
    #     return
    
    # # Extract article information from XML
    # # The structure follows the JATS (Journal Article Tag Suite) standard
    
    # # Get title
    # title_elem = root.find('.//article-title')
    # title_text = title_elem.text if title_elem is not None else f"PubMed Article PMC{pmcid}"

if __name__ == "__main__":
    # Testing
    create_epub_from_pubmed(doi="10.3390/biom13020339")
    create_epub_from_pubmed(pmid="36830707")
    create_epub_from_pubmed(pmcid="PMC9953331")
    # Error testing
    create_epub_from_pubmed(doi="jaja xd xd")
    create_epub_from_pubmed(pmid="10.3390/biom13020339")
    create_epub_from_pubmed(pmcid="PMC9953331",pmid="36830707")