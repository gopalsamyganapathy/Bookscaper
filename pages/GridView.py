import streamlit as st
from googleapiclient.discovery import build
import streamlit.components.v1 as components
import time
import MySQLdb
from MySQLdb import Error
import pandas as pd
#from IPython.display import display

st.set_page_config(
    page_title="Book Sales summary",
      # You can use an emoji or specify a path to an icon image
    layout="wide",   # options: 'centered' or 'wide'
    initial_sidebar_state="expanded"  # options: 'auto', 'expanded', 'collapsed'    
)

st.session_state.selection = 0


st.markdown("<h1 style='text-align: center; color: red; font-size: 60px;'>Book Sales Dashboard</h1>", unsafe_allow_html=True)

st.markdown("""<hr style="height:10px;border:none;color:#333;background-color:#FF0000;" /> """, unsafe_allow_html=True)



# option = st.selectbox(
#      'How would you like to be contacted?',
#      ('Email', 'Home phone', 'Mobile phone'))

# st.write('You selected:', option)


# Select box
selected = st.selectbox('Make a selection:', (
        'Check Availability of eBooks vs Physical Books',
        'Find the Publisher with the Most Books Published',
        'Identify the Publisher with the Highest Average Rating',
        'Get the Top 5 Most Expensive Books by Retail Price',
        'Find Books Published After 2010 with at Least 500 Pages',
        'List Books with Discounts Greater than 20%',
        'Find the Average Page Count for eBooks vs Physical Books',
        'Find the Top 3 Authors with the Most Books',
        'List Publishers with More than 10 Books',
        'Find the Average Page Count for Each Category',
        'Retrieve Books with More than 3 Authors',
        'Books with Ratings Count Greater Than the Average',
        'Books with the Same Author Published in the Same Year',
        'Books with a Specific Keyword in the Title',
        'Year with the Highest Average Book Price',
        'Count Authors Who Published 3 Consecutive Years',
        'Write a SQL query to find authors who have published books in the same year but under different publishers. Return the authors, year, and the COUNT of books they published in that year.',
        'Create a query to find the average amount_retailPrice of eBooks and physical books. Return a single result set with columns for avg_ebook_price and avg_physical_price. Ensure to handle cases where either category may have no entries.',
        'Write a SQL query to identify books that have an averageRating that is more than two standard deviations away from the average rating of all books. Return the title, averageRating, and ratingsCount for these outliers.',
        'Create a SQL query that determines which publisher has the highest average rating among its books, but only for publishers that have published more than 10 books. Return the publisher, average_rating, and the number of books published.'
    ), index=st.session_state['selection'])

def timeout_message(msg):
     time.sleep(3)
     msg.empty()

def create_db_connection_for_bookdb(host_name,user_name,user_password,db_name):
    print('inside bookdb up calling')
    conn = None    
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
       print(f"Db connection error {err}")
       timeout_message(st.error(f"Db connection error {err}", icon="🚨"))
       exit
    return conn

def execute_query(cursor,query):    
    try:
        
        cursor.execute(query)  
        records = cursor.fetchall()                 
        timeout_message(st.success('Query Execution SuccessFull', icon="✅"))
        return records
    except Error as err:
        timeout_message(st.error(f"Query Execution failed {err}", icon="🚨"))

print(f"Test {selected}")

dbconn = create_db_connection_for_bookdb("localhost","root","","book_db")
cursor = dbconn.cursor()
if(selected =='Check Availability of eBooks vs Physical Books'):
    query = """
                select CASE is_ebook
                WHEN 1 THEN 'Ebook'    
                ELSE "Physical book"
                END as Book,saleability as is_available, count(*) as total_qty  from book_summary where saleability ='FOR_SALE' group by is_ebook,saleability             
           """
    data_frame= pd.read_sql(query,dbconn)    
    data_frame.style
elif(selected == 'Find the Publisher with the Most Books Published'):
    query="SELECT PUBLISHER, COUNT(*) AS TOTAL_BOOK_PUBLISHED FROM BOOK_SUMMARY WHERE (PUBLISHER != '' AND PUBLISHER IS NOT NULL) GROUP BY PUBLISHER ORDER BY COUNT(*) DESC LIMIT 1"
    data_frame= pd.read_sql(query,dbconn)    
    data_frame.style
elif(selected == 'Identify the Publisher with the Highest Average Rating'):
    query="select Publisher,max(average_rating) as Highest_avg_Rating from book_summary where (PUBLISHER != '' AND PUBLISHER IS NOT NULL)"
    data_frame= pd.read_sql(query,dbconn)    
    data_frame.style
elif(selected == 'Get the Top 5 Most Expensive Books by Retail Price'):
    query="select book_title,amount_retail_price from book_summary order by amount_retail_price desc limit 5"
    data_frame= pd.read_sql(query,dbconn)    
    data_frame.style
elif(selected == 'Find Books Published After 2010 with at Least 500 Pages'):    
    query="select book_title,book_authors,YEAR(year) from book_summary where YEAR(year) >2010 and page_count >500"
    data_frame= pd.read_sql(query,dbconn)    
    data_frame.style
elif(selected == 'List Books with Discounts Greater than 20%'):
    query="select book_title,book_authors,amount_list_price, (amount_list_price * 0.2) as discount, (amount_list_price - ((amount_list_price * 0.2)))as actual_price, amount_retail_price from book_summary where amount_retail_price <(amount_list_price - ((amount_list_price * 0.2)))"
    data_frame= pd.read_sql(query,dbconn)    
    data_frame.style
elif(selected == 'Find the Average Page Count for eBooks vs Physical Books'):
    query="select CASE is_ebook WHEN 1 THEN 'Ebook' ELSE 'Physical book' END as Book, AVG(page_count) from book_summary group by Book"
    data_frame= pd.read_sql(query,dbconn)    
    data_frame.style
elif(selected == 'Find the Top 3 Authors with the Most Books'):
    query="select book_authors, count(*) as total_books from book_summary where (book_authors != '' AND book_authors IS NOT NULL) group by book_authors order by count(*) desc  limit 3"
    data_frame= pd.read_sql(query,dbconn)    
    data_frame.style
elif(selected == 'List Publishers with More than 10 Books'):
    query="select Publisher , count(*) as total_books from book_summary where (PUBLISHER != '' AND PUBLISHER IS NOT NULL)  group by Publisher having count(*)>=10"
    data_frame= pd.read_sql(query,dbconn)    
    data_frame.style
elif(selected == 'Find the Average Page Count for Each Category'):
    query = "select categories, AVG(page_count) as AVG_PAGE_COUNT from book_summary group by categories order by AVG(page_count) desc limit 10"
    data_frame= pd.read_sql(query,dbconn)    
    data_frame.style
elif(selected == 'Retrieve Books with More than 3 Authors'):
    query="select book_title from book_summary where  (book_authors != '' AND book_authors IS NOT NULL) group by book_title having count(book_authors)>2 order by count(book_authors) desc"
    data_frame= pd.read_sql(query,dbconn)    
    data_frame.style
elif(selected == 'Books with Ratings Count Greater Than the Average'):
    query="select book_title,rating_Count,average_rating from book_summary where rating_Count >average_rating"
    data_frame= pd.read_sql(query,dbconn)    
    data_frame.style
elif(selected == 'Books with the Same Author Published in the Same Year'):
    query="select book_title,book_authors,Year from book_summary where (book_authors != '' AND book_authors IS NOT NULL) group by book_authors,Year"
    data_frame= pd.read_sql(query,dbconn)    
    data_frame.style
elif(selected == 'Books with a Specific Keyword in the Title'):
    query = "select book_title, search_key from book_summary where lower(book_title) like '%python%'"
    data_frame= pd.read_sql(query,dbconn)    
    data_frame.style
elif(selected == 'Year with the Highest Average Book Price'):
    query="select year,avg(amount_retail_price) from book_summary where (year != '' AND year IS NOT NULL) order by avg(amount_retail_price) desc"
    data_frame= pd.read_sql(query,dbconn)    
    data_frame.style
elif(selected == 'Count Authors Who Published 3 Consecutive Years'):
    query= """
        WITH ConsecutiveYears AS (
                SELECT
                *,
                LAG(year, 1) OVER (PARTITION BY book_authors ORDER BY year) AS prev_year,
                LAG(year, 2) OVER (PARTITION BY book_authors ORDER BY year) AS prev_prev_year
                FROM
                book_summary
        )
        SELECT DISTINCT book_authors,YEAR(year),YEAR(prev_year),YEAR(prev_prev_year)
        FROM ConsecutiveYears
        WHERE
        YEAR(prev_year) = (YEAR(prev_prev_year) +1) AND
        YEAR(year) = (YEAR(prev_year) +1)          
          """
    data_frame= pd.read_sql(query,dbconn)    
    data_frame.style
elif(selected == 'Write a SQL query to find authors who have published books in the same year but under different publishers. Return the authors, year, and the COUNT of books they published in that year.'):
    query = """WITH YearPublisherCounts AS (
                        SELECT
                                book_authors,
                                year(year) as year,
                                        publisher,
                                COUNT(*) AS book_count
                                FROM
                                        book_summary where (book_authors != '' AND book_authors IS NOT NULL)
                                GROUP BY
                                        book_authors,
                                        year(year)
                )
                SELECT
                y.book_authors,
                y.year,
                book_count
                FROM
                YearPublisherCounts y
                        inner join book_summary b on b.book_authors = y.book_authors and year(b.year)=year
                        where (publisher != '' AND publisher IS NOT NULL)
                y.publisher<> b.publisher and book_count > 1
        """
    data_frame= pd.read_sql(query,dbconn)    
    data_frame.style
elif(selected == 'Create a query to find the average amount_retailPrice of eBooks and physical books. Return a single result set with columns for avg_ebook_price and avg_physical_price. Ensure to handle cases where either category may have no entries.'):
    query= """SELECT
                AVG(CASE WHEN is_ebook = 1 THEN amount_retailPrice END) AS avg_ebook_price,
                AVG(CASE WHEN is_ebook = 0 THEN amount_retailPrice END) AS avg_physical_price
                FROM
                book_summary
            """
    data_frame= pd.read_sql(query,dbconn)    
    data_frame.style
elif(selected == 'Write a SQL query to identify books that have an averageRating that is more than two standard deviations away from the average rating of all books. Return the title, averageRating, and ratingsCount for these outliers.'):
    query="""
                SELECT
                        book_title,
                        average_rating,
                        ratings_count
                FROM
                book_summary
                WHERE
                average_rating > (SELECT AVG(average_rating) + 2 * STDDEV(average_rating) FROM book_summary)
                OR
                average_rating < (SELECT AVG(average_rating) - 2 * STDDEV(average_rating) FROM book_summary)                      
          """
    data_frame= pd.read_sql(query,dbconn)    
    data_frame.style
elif(selected == 'Create a SQL query that determines which publisher has the highest average rating among its books, but only for publishers that have published more than 10 books. Return the publisher, average_rating, and the number of books published'):
    query="""
                SELECT
                        publisher,
                        AVG(average_rating) AS average_rating,
                        COUNT(*) AS book_count
                FROM
                        book_summary where (publisher != '' AND publisher IS NOT NULL)
                GROUP BY
                        publisher
                HAVING
                        COUNT(*) > 10
                ORDER BY
                        average_rating DESC
                LIMIT 1
     """
    data_frame= pd.read_sql(query,dbconn)    
    data_frame.style
