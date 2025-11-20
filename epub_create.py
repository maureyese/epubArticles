import xml.etree.ElementTree as ET
from ebooklib import epub

def add_metadata_to_epub(root, book):
    # Language
    language = root.get('{http://www.w3.org/XML/1998/namespace}lang', 'en')
    book.set_language(language)
    
    # Identifier (DOI)
    doi_elem = root.find('.//article-id[@pub-id-type="doi"]')
    if doi_elem is not None:
        book.set_identifier(doi_elem.text)
    
    # Authors
    authors = []
    contrib_group = root.find('.//contrib-group')
    if contrib_group is not None:
        for contrib in contrib_group.findall('.//contrib[@contrib-type="author"]'):
            surname_elem = contrib.find('.//surname')
            given_names_elem = contrib.find('.//given-names')
            if surname_elem is not None and given_names_elem is not None:
                author_name = f"{surname_elem.text}, {given_names_elem.text}"
                authors.append(author_name)
    
    if authors:
        book.add_author("; ".join(authors))
    
    # Title
    title_elem = root.find('.//article-title')
    if title_elem is not None:
        title_text = ''.join(title_elem.itertext()).strip()
        book.set_title(title_text)
    
    return book

def add_cover_to_epub(book, cover_image_path="banners/logo-nihpa.png", cover_title=None):
    """
    Add a cover to the EPUB book
    
    Args:
        book: epub.EpubBook object
        cover_image_path: Path to local cover image (optional)
        cover_title: Title for the cover page (optional)
    """
    # TODO: Improve cover

    # Create a simple cover page with title and authors
    if cover_title is None:
        cover_title = book.title if book.title else "Scientific Article"
    
    cover_content = f"""
    <html>
        <head>
            <title>Cover</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    text-align: center;
                    margin: 0;
                    padding: 30px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    min-height: 80vh;
                }}
                .logo {{
                    margin-bottom: 30px;
                }}
                .logo img {{
                    max-width: 200px;
                    height: auto;
                }}
                h1 {{
                    font-size: 2.2em;
                    margin-bottom: 20px;
                    color: #333;
                    line-height: 1.3;
                }}
                .authors {{
                    font-size: 1.2em;
                    color: #666;
                    margin-bottom: 25px;
                    line-height: 1.4;
                }}
                .doi {{
                    font-size: 1em;
                    color: #999;
                    margin-top: 30px;
                    font-style: italic;
                }}
                .separator {{
                    width: 80%;
                    height: 2px;
                    background-color: #ddd;
                    margin: 20px auto;
                }}
            </style>
        </head>
        <body>
            <div class="logo">
                <img src="images/logo-nihpa.png" alt="NIH Logo" />
            </div>
            <div class="separator"></div>
            <h1>{cover_title}</h1>
            <div class="authors">
                {book.get_metadata('DC', 'creator')[0][0] if book.get_metadata('DC', 'creator') else ''}
            </div>
            <div class="separator"></div>
            <div class="doi">
                {book.get_metadata('DC', 'identifier')[0][0] if book.get_metadata('DC', 'identifier') else ''}
            </div>
        </body>
    </html>
    """
    
    # Create cover chapter
    cover_page = epub.EpubHtml(title='Cover', file_name='cover.xhtml', lang='en')
    cover_page.content = cover_content
    
    # Add cover page to book
    book.add_item(cover_page)
    
    # Add local cover image if path provided and file exists
    if cover_image_path:
        try:
            with open(cover_image_path, 'rb') as img_file:
                image_content = img_file.read()
                
            # Determine image type from file extension
            if cover_image_path.lower().endswith('.png'):
                image_type = 'png'
                file_name = 'images/logo-nihpa.png'
            elif cover_image_path.lower().endswith(('.jpg', '.jpeg')):
                image_type = 'jpeg'
                file_name = 'images/logo-nihpa.jpg'
            else:
                image_type = 'png'  # default
                file_name = 'images/logo-nihpa.png'
            
            # Create image item
            cover_image = epub.EpubImage(
                uid='nih_logo',
                file_name=file_name,
                media_type=f'image/{image_type}',
                content=image_content
            )
            book.add_item(cover_image)
            print(f"Successfully added NIH logo from: {cover_image_path}")
            
        except FileNotFoundError:
            print(f"Warning: Cover image not found at {cover_image_path}")
        except Exception as e:
            print(f"Warning: Could not add cover image: {e}")
    
    # Set cover page as the first item in spine
    book.spine = ['cover'] + book.spine
    
    return book

def create_epub_file(root):
    '''
    Convert XML PubMed file to EPUB
    '''
    # Set book
    book = epub.EpubBook()

    # Add metadata
    book = add_metadata_to_epub(root=root, book=book)

    # Add cover
    book = add_cover_to_epub(book=book)
    
    return book

if __name__ == "__main__":
    # Open and parse the XML file
    try:
        tree = ET.parse('debugging.xml')
        root = tree.getroot()
        
        # Test the function
        book = create_epub_file(root)
        
        # Print metadata to verify
        print("EPUB Metadata:")
        print(f"Title: {book.title}")
        print(f"Language: {book.language}")
        print(f"Identifier: {book.get_metadata('DC', 'identifier')}")
        print(f"Authors: {book.get_metadata('DC', 'creator')}")
        
    except FileNotFoundError:
        print("Error: debugging.xml file not found. Please make sure the file exists.")
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    
    # Write to a file
    epub.write_epub('test.epub', book)