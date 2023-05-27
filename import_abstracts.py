import os
import pickle
import psycopg
from pgvector.psycopg import register_vector
from tqdm import tqdm

DIRNAME = os.path.dirname(__file__)

with psycopg.connect("dbname=arxiv") as conn:
    register_vector(conn)
    with conn.cursor() as cur:

        # First lets create the table
        print("Creating table abstracts if it doesn't exist")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS abstracts (
                doi text PRIMARY KEY,
                abstract text,
                embedding vector(768))
            """)
        print("Table created")

        for i in range(0, 23):
            path = os.path.join(DIRNAME, f'arxiv_abstracts/embeddings_{i}.pkl')
            print(f'Reading file {path}')
            with open(path, "rb") as pkl_file:
                data = pickle.load(pkl_file)

            print(f'Starting postgres import of {path}')
            for batch in tqdm(data):
                abstract, embedding, doi = batch
                cur.execute(
                    "INSERT INTO abstracts (doi, abstract, embedding) VALUES (%s, %s, %s)",
                    (doi, abstract, embedding)
                )

            print(f'Finished postgres import of {path}')

        conn.commit()
                
                
print("Finished import")
