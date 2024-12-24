import streamlit as st
from googleapiclient.discovery import build
import time
import MySQLdb
from MySQLdb import Error
from datetime import date
import sqlalchemy as sa
import threading


# Replace with your actual API key
API_KEY = "AIzaSyBanLmtOtWhX3yBscUhW4KhmjoihS7tUIM" 
# Set the page title and other configurations
st.set_page_config(
    page_title="Book summary",
    page_icon="🏠",  # You can use an emoji or specify a path to an icon image
    layout="wide",   # options: 'centered' or 'wide'
    initial_sidebar_state="expanded"  # options: 'auto', 'expanded', 'collapsed'    
)

st.markdown("<h1 style='text-align: center; color: red; font-size: 60px;'>Book Summary</h1>", unsafe_allow_html=True)

st.markdown("""<hr style="height:10px;border:none;color:#333;background-color:#FF0000;" /> """, unsafe_allow_html=True)


def timeout_message(msg):
    time.sleep(3)
    msg.empty()

def create_db_connection_for_bookdb(host_name,user_name,user_password,db_name):
    print('inside bookdb up calling')
    try:
        conn = MySQLdb.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
            )
        print("MySQL Database connection successFull for" + db_name)        
        timeout_message(st.success('DB connection Obtained', icon="✅"))
    except Error as err:
          timeout_message(st.error(f"Db connection error {err}", icon="🚨"))  
          conn.close        
    return conn

def execute_query(conn,query):    
    try:
        cursor = conn.cursor()
        cursor.execute(query)        
        timeout_message(st.success('Query Execution SuccessFull', icon="✅"))
    except Error as err:        
        timeout_message(st.error(f"Query Execution failed {err}", icon="🚨"))
    finally:
        conn.commit()      
        conn.close()  

# Function to fetch book data from Google Books API
def getISBN13Dist(obj):
    isbn_13=''
    for i in obj:
        identifier_type = i['type']
        identifier_value = i['identifier']
        if identifier_type == 'ISBN_13':
                isbn_13 =identifier_value
    return isbn_13

    
def setEmptyResponseObj(x):
  if 'publisher' not in x['volumeInfo']:
    x['volumeInfo']['publisher']=''
  if 'industryIdentifiers' not in x['volumeInfo']:
     x['volumeInfo']['industryIdentifiers']=[]
  if 'subtitle' not in x['volumeInfo']:
    x['volumeInfo']['subtitle']=''
  if 'categories' not in x['volumeInfo']:
    x['volumeInfo']['categories']=''
  if 'publishedDate' not in x['volumeInfo']:
    x['volumeInfo']['publishedDate']=''
  if "description" not in x['volumeInfo']:
    x['volumeInfo']['description']=''
  if "ratingsCount" not in x['volumeInfo']:
    x['volumeInfo']['ratingsCount']=''
  if "averageRating" not in x['volumeInfo']:
    x['volumeInfo']['averageRating']='' 
  if 'listPrice' not in x['saleInfo']:
     x['saleInfo']['listPrice']={}
     x['saleInfo']['listPrice']['amount']=''
     x['saleInfo']['listPrice']['currencyCode']=''
  if 'retailPrice' not in x['saleInfo']:
     x['saleInfo']['retailPrice']={}
     x['saleInfo']['retailPrice']['amount']=''
     x['saleInfo']['retailPrice']['currencyCode']=''
  if 'buyLink' not in x['saleInfo']:
     x['saleInfo']['buyLink']=None

def check_data (cursor,book_id):
    check_query = "SELECT COUNT(*) FROM book_summary WHERE book_id = %s"
    cursor.execute(check_query, (book_id, ))
    row_count = cursor.fetchone()[0]  
    return row_count

def insert_book_data(cursor, x, search_key):
    setEmptyResponseObj(x)

    book_id = x.get('id', None)  
    publisher = (x['volumeInfo'].get('publisher', None))
    book_title = (x['volumeInfo'].get('title', None))
    book_subtitle = (x['volumeInfo'].get('subtitle', None))
    book_authors = ",".join((author) for author in x['volumeInfo'].get('authors', ''))
    book_description = (x['volumeInfo'].get('description', None))
    industry_identifiers = getISBN13Dist(x['volumeInfo']['industryIdentifiers'])
    text_reading_modes = x['volumeInfo'].get('readingModes', {}).get('text', False)
    image_reading_modes = x['volumeInfo'].get('readingModes', {}).get('image', False)    
    page_count = int(x['volumeInfo'].get('pageCount', 0)) if x['volumeInfo'].get('pageCount', '') != '' else 0
    categories = ",".join((category) for category in x['volumeInfo'].get('categories', ''))
    language = (x['volumeInfo'].get('language', None))
    preview_link = (x['volumeInfo'].get('previewLink', None))    
    ratings_count = int(x['volumeInfo'].get('ratingsCount', 0)) if x['volumeInfo'].get('ratingsCount', '') != '' else 0
    average_rating = (x['volumeInfo'].get('averageRating', 0.0))  # Convert to float
    country = (x['saleInfo'].get('country', None))
    saleability = (x['saleInfo'].get('saleability', None))
    is_ebook = bool(x['saleInfo'].get('isEbook', False))    
    list_price_currency = (x['saleInfo']['listPrice'].get('currencyCode', None))    
    retail_price_currency = (x['saleInfo']['retailPrice'].get('currencyCode', None))
    buy_link = (x['saleInfo'].get('buyLink', None))
    current_year = date.today().year
    published_date_api = x['volumeInfo'].get('publishedDate', date.today().year)
    published_date = (published_date_api[:4])  if len(published_date_api[:4]) == 4 else current_year
    amount_list_price = float(x['saleInfo']['listPrice'].get('amount', 0.0)) if x['saleInfo']['listPrice'].get('amount', '') != '' else 0.0
    retail_price_amount = float(x['saleInfo']['retailPrice'].get('amount', 0.0)) if x['saleInfo']['retailPrice'].get('amount', '') != '' else 0.0
     
    row_count = check_data(cursor,book_id)
    if row_count == 0:
        cursor.execute("INSERT INTO book_summary (book_id,publisher, search_key, book_title,book_subtitle,book_authors,book_description,industry_identifiers,text_reading_modes,image_reading_modes,page_count,categories,language,preview_link,ratings_count,average_rating,country,saleability, is_ebook, amount_list_price,currencyCode_list_price,amount_retail_price, currencyCode_retail_price,buy_link,year) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (book_id,publisher, search_key, book_title,book_subtitle,book_authors,book_description,industry_identifiers,text_reading_modes,image_reading_modes,page_count,categories,language,preview_link,ratings_count,average_rating,country,saleability, is_ebook, amount_list_price,list_price_currency,retail_price_amount, retail_price_currency,buy_link,published_date, ))
    else:        
        print(f'Duplicate Primary Key found skipping it   -{book_id}')  


# Main function to fetch and store book data
def fetch_and_store_data(cursor,query, num_books):

    max_results_per_page = 40  # Adjust as needed
    num_pages = (num_books // max_results_per_page) + 1
    for i in range(num_pages):
        startIndex = i * max_results_per_page
        time.sleep(0.05)
        get_book_data(query,cursor, max_results=max_results_per_page, startIndex=startIndex)


def get_book_data(query,cursor, max_results=40, startIndex=0):
    
    try:
        service = build('books', 'v1', developerKey=API_KEY)
        results = service.volumes().list(q=query, maxResults=max_results, startIndex=startIndex).execute()

        items = results.get('items', [])
        book_data = []
        
        for x in items:
           insert_book_data(cursor,x,query)
        return book_data

    except Error as e:
        print(f"Error fetching data: {e}")
        



# if "clicked" not in st.session_state:
#     st.session_state["clicked"] = False

def drawBtn():
    option= ...
    st.button("Clean Up", args= [option])


# def searchbook():
#     print(st.session_state.text_key)
#     query = st.session_state.text_key
#     num_books_to_fetch = 1500
#     with st.spinner('Wait for it...Data inserting'):
#         time.sleep(5)
#     try:
#         dbconn = create_db_connection_for_bookdb("localhost","root","","book_db")
#         # cursor = dbconn.cursor()
#         fetch_and_store_data(dbconn.cursor(),query, num_books_to_fetch)                     
#         # su =st.success("Done!")
#         timeout_message(st.success('Records Are Inserted Successfully', icon="✅"))
#         # su.empty()
#     except Exception as err:
#        print(f"Db connection error {err}")
#        timeout_message(st.error(f"Db connection error {err}", icon="🚨"))
#        exit() 
#     finally:
#         dbconn.commit()
#         dbconn.close()    

def searchbook():
    """
    Handles the search button click.
    """
    query = st.session_state.text_key
    num_books_to_fetch = 1500

    with st.spinner('Wait for it...Data inserting'):
        try:
            dbconn = create_db_connection_for_bookdb("localhost","root","","book_db")
            # Create and start a thread for data insertion
            thread = threading.Thread(target=fetch_and_store_data, args=(dbconn.cursor(), query, num_books_to_fetch))
            thread.start()

            # Wait for the thread to finish
            thread.join() 

            timeout_message(st.success('Records Are Inserted Successfully', icon="✅"))

        except Exception as err:
            print(f"Db connection error {err}")
            timeout_message(st.error(f"Db connection error {err}", icon="🚨"))
        finally:
            dbconn.commit()
            dbconn.close()



# when we click the cleanup button, it calls this method
def cleanup():    
    try:
        dbconn = create_db_connection_for_bookdb("localhost","root","","book_db")
        if dbconn is not None:
            execute_query(dbconn,"DELETE FROM book_summary")                      
    except Error as err:
        timeout_message(st.error(f"Query Execution failed {err}", icon="🚨"))
        print(err)    

# The block which is helping to render the side menu
left, middle = st.columns(2)
option= ...
if left.button("Clean Up", use_container_width=True, args= [option]):
     cleanup()        
if middle.button("Search",  use_container_width=True):
    search_book = st.text_input("Please serch something",placeholder='enter to continue',on_change=searchbook,key='text_key')  
