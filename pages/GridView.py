import streamlit as st
from googleapiclient.discovery import build
import streamlit.components.v1 as components
import time
import MySQLdb
from MySQLdb import Error
import pandas as pd
import sqlalchemy as sa

st.set_page_config(
    page_title="Book Sales summary",
    layout="wide",  
    initial_sidebar_state="expanded"    
)


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
          timeout_message(st.error(f"Db connection error {err}", icon="🚨"))
          exit()
    return conn

st.session_state.selection = 0


st.markdown("<h1 style='text-align: center; color: red; font-size: 60px;'>Book Sales Dashboard</h1>", unsafe_allow_html=True)

st.markdown("""<hr style="height:10px;border:none;color:#333;background-color:#FF0000;" /> """, unsafe_allow_html=True)


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

def rederSQLdata(query,dbconn):
    try:
        data_frame= pd.read_sql(query,dbconn)    
        data_frame.style
    except Error as err:
        print('**panda rendering**')


dbconn = create_db_connection_for_bookdb("localhost","root","","book_db")
cursor = dbconn.cursor()
if(selected =='Check Availability of eBooks vs Physical Books'):
    query = """
                SELECT CASE IS_EBOOK
                WHEN 0 THEN 'PHYSCIAL-BOOK'    
                ELSE "E-BOOK"
                END AS BOOK,SALEABILITY AS SALE_STATUS, COUNT(*) AS TOTAL_BOOKS  FROM BOOK_SUMMARY WHERE SALEABILITY ='FOR_SALE' GROUP BY IS_EBOOK,SALEABILITY             
           """
    rederSQLdata(query,dbconn)    
    
elif(selected == 'Find the Publisher with the Most Books Published'):
    query="SELECT PUBLISHER, COUNT(*) AS TOTAL_BOOK_PUBLISHED FROM BOOK_SUMMARY WHERE (PUBLISHER != '' AND PUBLISHER IS NOT NULL) GROUP BY PUBLISHER ORDER BY COUNT(*) DESC LIMIT 1"
    rederSQLdata(query,dbconn)    
    
elif(selected == 'Identify the Publisher with the Highest Average Rating'):
    query="SELECT PUBLISHER,MAX(AVERAGE_RATING) AS HIGHEST_AVG_RATING FROM BOOK_SUMMARY WHERE (PUBLISHER != '' AND PUBLISHER IS NOT NULL)"
    rederSQLdata(query,dbconn)    
    
elif(selected == 'Get the Top 5 Most Expensive Books by Retail Price'):
    QUERY="SELECT BOOK_TITLE,AMOUNT_RETAIL_PRICE FROM BOOK_SUMMARY ORDER BY AMOUNT_RETAIL_PRICE DESC LIMIT 5"
    rederSQLdata(QUERY,dbconn)    
    
elif(selected == 'Find Books Published After 2010 with at Least 500 Pages'):    
    QUERY="SELECT BOOK_TITLE,BOOK_AUTHORS,YEAR(YEAR) FROM BOOK_SUMMARY WHERE YEAR(YEAR) >2010 AND PAGE_COUNT >500"
    rederSQLdata(QUERY,dbconn)    
    
elif(selected == 'List Books with Discounts Greater than 20%'):
    QUERY="SELECT BOOK_TITLE,BOOK_AUTHORS,AMOUNT_LIST_PRICE, (AMOUNT_LIST_PRICE * 0.2) AS DISCOUNT, (AMOUNT_LIST_PRICE - ((AMOUNT_LIST_PRICE * 0.2)))AS ACTUAL_PRICE, AMOUNT_RETAIL_PRICE FROM BOOK_SUMMARY WHERE AMOUNT_RETAIL_PRICE <(AMOUNT_LIST_PRICE - ((AMOUNT_LIST_PRICE * 0.2)))"
    rederSQLdata(QUERY,dbconn)    
    
elif(selected == 'Find the Average Page Count for eBooks vs Physical Books'):
    QUERY="SELECT CASE IS_EBOOK WHEN 1 THEN 'EBOOK' ELSE 'PHYSICAL BOOK' END AS BOOK, AVG(PAGE_COUNT) as AVG_PAGE_COUNT FROM BOOK_SUMMARY GROUP BY BOOK"
    rederSQLdata(QUERY,dbconn)    
    
elif(selected == 'Find the Top 3 Authors with the Most Books'):
    QUERY="SELECT BOOK_AUTHORS, COUNT(*) AS TOTAL_BOOKS FROM BOOK_SUMMARY WHERE (BOOK_AUTHORS != '' AND BOOK_AUTHORS IS NOT NULL) GROUP BY BOOK_AUTHORS ORDER BY COUNT(*) DESC  LIMIT 3"
    rederSQLdata(QUERY,dbconn)    
    
elif(selected == 'List Publishers with More than 10 Books'):
    QUERY="SELECT PUBLISHER , COUNT(*) AS TOTAL_BOOKS FROM BOOK_SUMMARY WHERE (PUBLISHER != '' AND PUBLISHER IS NOT NULL)  GROUP BY PUBLISHER HAVING COUNT(*)>=10"
    rederSQLdata(QUERY,dbconn)    
    
elif(selected == 'Find the Average Page Count for Each Category'):
    QUERY = "SELECT CATEGORIES, AVG(PAGE_COUNT) AS AVG_PAGE_COUNT FROM BOOK_SUMMARY GROUP BY CATEGORIES ORDER BY AVG(PAGE_COUNT) DESC"
    rederSQLdata(QUERY,dbconn)    
    
elif(selected == 'Retrieve Books with More than 3 Authors'):
    QUERY="SELECT BOOK_TITLE FROM BOOK_SUMMARY WHERE  (BOOK_AUTHORS != '' AND BOOK_AUTHORS IS NOT NULL) GROUP BY BOOK_TITLE HAVING COUNT(BOOK_AUTHORS)>2 ORDER BY COUNT(BOOK_AUTHORS) DESC"
    rederSQLdata(QUERY,dbconn)    
    
elif(selected == 'Books with Ratings Count Greater Than the Average'):
    QUERY="SELECT BOOK_TITLE,RATING_COUNT,AVERAGE_RATING FROM BOOK_SUMMARY WHERE RATING_COUNT >AVERAGE_RATING"
    rederSQLdata(QUERY,dbconn)    
    
elif(selected == 'Books with the Same Author Published in the Same Year'):
    query="select book_title,book_authors,Year from book_summary where (book_authors != '' AND book_authors IS NOT NULL) group by book_authors,Year"
    rederSQLdata(query,dbconn)    
    
elif(selected == 'Books with a Specific Keyword in the Title'):
    QUERY = "SELECT BOOK_TITLE, SEARCH_KEY FROM BOOK_SUMMARY WHERE LOWER(BOOK_TITLE) LIKE '%PYTHON%'"
    rederSQLdata(QUERY,dbconn)    
    
elif(selected == 'Year with the Highest Average Book Price'):
    QUERY="SELECT YEAR,AVG(AMOUNT_RETAIL_PRICE) as Highest_AVG_PRICE FROM BOOK_SUMMARY WHERE (YEAR != '' AND YEAR IS NOT NULL) ORDER BY AVG(AMOUNT_RETAIL_PRICE) DESC"
    rederSQLdata(QUERY,dbconn)    
    
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
    rederSQLdata(query,dbconn)    
    
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
    rederSQLdata(query,dbconn)    
    
elif(selected == 'Create a query to find the average amount_retailPrice of eBooks and physical books. Return a single result set with columns for avg_ebook_price and avg_physical_price. Ensure to handle cases where either category may have no entries.'):
    query= """SELECT
                AVG(CASE WHEN is_ebook = 1 THEN amount_retailPrice END) AS avg_ebook_price,
                AVG(CASE WHEN is_ebook = 0 THEN amount_retailPrice END) AS avg_physical_price
                FROM
                book_summary
            """
    rederSQLdata(query,dbconn)    
    
elif(selected == 'Write a SQL query to identify books that have an averageRating that is more than two standard deviations away from the average rating of all books. Return the title, averageRating, and ratingsCount for these outliers.'):
    query="""
                 SELECT
                        BOOK_TITLE,
                        AVERAGE_RATING,
                        RATINGS_COUNT
                FROM
                BOOK_SUMMARY
                WHERE
                AVERAGE_RATING > (SELECT AVG(AVERAGE_RATING) + 2 * STDDEV(AVERAGE_RATING) FROM BOOK_SUMMARY)
                OR
                AVERAGE_RATING < (SELECT AVG(AVERAGE_RATING) - 2 * STDDEV(AVERAGE_RATING) FROM BOOK_SUMMARY)                       
          """
    rederSQLdata(query,dbconn)    
    
elif(selected == 'Create a SQL query that determines which publisher has the highest average rating among its books, but only for publishers that have published more than 10 books. Return the publisher, average_rating, and the number of books published'):
    query="""
                SELECT
                        PUBLISHER,
                        AVG(AVERAGE_RATING) AS AVERAGE_RATING,
                        COUNT(*) AS BOOK_COUNT
                FROM
                        BOOK_SUMMARY WHERE (PUBLISHER != '' AND PUBLISHER IS NOT NULL)
                GROUP BY
                        PUBLISHER
                HAVING
                        COUNT(*) > 10
                ORDER BY
                        AVERAGE_RATING DESC
                LIMIT 1
     """
    rederSQLdata(query,dbconn)    
    
