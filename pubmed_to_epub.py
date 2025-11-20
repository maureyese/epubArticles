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
        - pmid:str
            PubMed ID (e.g., "36830707")
        - doi:str
            DOI (e.g., "10.3390/biom13020339")

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
    fetch_url = f"{base_url}efetch.fcgi"

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
            'term': f"{pmid}[pmid]",
            'retmode': 'json'
        }

        try:
            response = requests.get(search_url, params=search_params)
            response.raise_for_status()
            search_data = response.json()
            if not search_data['esearchresult']['idlist']:
                print(f"No article found for PMID: {pmid}")
                return None
            pmcid = search_data['esearchresult']['idlist'][0]
            print(f"PMID {pmid} converted to PMCID: {pmcid}")
        except requests.exceptions.RequestException as e:
            print(f"Error during request: {e}")
            return None

    # ---------------------------------
    # PMCID (Full-text)
    # ---------------------------------

    if pmcid:
        # Remove "PMC" prefix
        pmcid = pmcid.upper().replace("PMC", "").strip()
        if not pmcid.isdigit():
            print(f"Invalid PMCID detected ({pmcid}). Try user other argument (pmid, or doi).")
            return None
        print(f"PMCID detected: PMC{pmcid}")

        # Fetch full article data in XML format
        fetch_params = {
            'db': 'pmc',
            'id': pmcid,
            'retmode': 'xml'
        }

        print(f"Fetching XML for PMCID: PMC{pmcid}...")

        try:
            fetch_response = requests.get(fetch_url, params=fetch_params, timeout=60)
            fetch_response.raise_for_status()
            print("Found article information. Trying to convert to XML...")

            # Check if we got valid content
            if not fetch_response.content:
                print("No content received from server")
                return None

            try:
                root = ET.fromstring(fetch_response.content)
                print(f"Successfully parsed XML. Root tag: {root.tag}")

                # Print title article
                article_title = root.find('.//article-title')
                if article_title is not None:
                    print(f"Article title: {''.join(article_title.itertext())}")
                else:
                    print("No article title found")

                # create_epub_file(root, pmcid)
                with open('debugging.txt', "w") as t:
                    t.write(fetch_response.text)

            except ET.ParseError as e:
                print(f"Error parsing content as XML: {e}")
                print(f"First 500 characters of response: {fetch_response.text[:500]}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching full text for PMCID {pmcid}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
    else:
        print("PMCID not found.")
        return None

if __name__ == "__main__":
    print("--- Test Case: DOI (Successful Path) ---")
    create_epub_from_pubmed(doi="10.3390/biom13020339")

    print("\n--- Test Case: Direct PMCID ---")
    create_epub_from_pubmed(pmcid="PMC9953331")

    print("\n--- Test Case: Invalid PMID Format (Validation Check) ---")
    create_epub_from_pubmed(pmid="invalid-id-string")