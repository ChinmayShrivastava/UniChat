import openai
import pinecone
import langchain
import psycopg2
from .getembeddings import get_dense_vector, get_sparse_vector
import os

DATABASE_URL = os.environ['SQL_URL']
# connect to postgres
conn = psycopg2.connect(DATABASE_URL)
# create a cursor
cur = conn.cursor()

openai.api_key = os.getenv('OPENAI_API_KEY')

PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_ENV = os.getenv('PINECONE_ENV')
PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME')

# connect to pinecone
pinecone.init(
    api_key=PINECONE_API_KEY,
    environment=PINECONE_ENV
)

# connect to pinecone index
index = pinecone.Index(PINECONE_INDEX_NAME)

# set alpha for hybrid score
alpha_dense_more = 0.75
alpha_sparse_more = 0.25

def hybrid_score_norm(dense, sparse, alpha: float):
    """Hybrid score using a convex combination

    alpha * dense + (1 - alpha) * sparse

    Args:
        dense: Array of floats representing
        sparse: a dict of `indices` and `values`
        alpha: scale between 0 and 1
    """
    if alpha < 0 or alpha > 1:
        raise ValueError("Alpha must be between 0 and 1")
    hs = {
        'indices': sparse['indices'],
        'values':  [v * (1 - alpha) for v in sparse['values']]
    }
    return [v * alpha for v in dense], hs

def insert_vector(dense_vector, sparse_vector, domain, nameSpace='unichat'):

    # index the vector
    upsert_response = index.upsert(
        vectors=[
            {
                'domain': domain,
                'values': dense_vector,
                'sparse_values': sparse_vector,
            }
        ],
        namespace = nameSpace
    )

    return upsert_response

def is_copy_url(url):
    # check if URL has queries
    if '?' in url:
        return True, url.split('?')[0]
    # check if URL has a hash at the end
    split_url = url.split('/')
    last_element = split_url[-1]
    if '#' in last_element:
        return True, url.split('#')[0]
    # return the url without the hash or queries
    return False, url

def select_row_by_index(index, tablename, columnname, conn):
    with conn.cursor() as cur:
        cur.execute(f"SELECT {columnname} FROM {tablename} LIMIT 1 OFFSET %s", (index,))
        row = cur.fetchone()
        return row

def get_url_by_headingid(rowid, conn):
    with conn.cursor() as cur:
        heading = cur.execute("SELECT urlid FROM headings WHERE rowid = %s", (rowid,))
        heading = cur.fetchone()
    url = select_row_by_index(heading[0], 'urls', '*', conn)
    return url # list of items related to the url


def get_heading_by_rowid(rowid, cur): # row id is the same as pineconeid here
    cur.execute("SELECT * FROM headings WHERE rowid = %s", (rowid,))
    heading = cur.fetchone()
    return heading # list of items related to the heading

def embed():

    # get all the urls where embedded is false
    cur.execute("SELECT url FROM urls WHERE embedded = false")
    urls = cur.fetchall()

    # loop through the urls
    i=0
    for url in urls:
        i+=1
        print(i)
        # get the url
        url = url[0]
        # check if the url is a copy
        is_copy, url = is_copy_url(url)
        if is_copy:
            if url in urls:
                # mark the url as embedded
                cur.execute("UPDATE urls SET embedded = true WHERE url = %s", (url,))
                conn.commit()
                continue
        # get the dense and sparse vectors
        dense_vector = get_dense_vector(url)
        sparse_vector = get_sparse_vector(url)
        # insert the vector into pinecone
        insert_vector(dense_vector, sparse_vector, url)
        # mark the url as embedded
        cur.execute("UPDATE urls SET embedded = true WHERE url = %s", (url,))
        conn.commit()

if __name__ == '__main__':
    embed()