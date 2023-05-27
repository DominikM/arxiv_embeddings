from InstructorEmbedding import INSTRUCTOR
import psycopg
import signal
import sys
from pgvector.psycopg import register_vector
from tabulate import tabulate

def signal_handler(sig, frame):
    print("quitting...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def get_query(question):
    return [['Represent the Research Paper question for retrieving supporting abstracts: ', question]]

def get_embedding(model, question):
    return model.encode(get_query(question))[0]

def print_results(results):
    print(tabulate([result[0] for result in results], headers=['title', 'doi']))

def loop(model, cur):
    while True:
            question = input("What is your question? ")
            embedding = get_embedding(model, question)            

            results = cur.execute(
                'SELECT (titles.title, titles.doi) FROM titles JOIN abstracts ON titles.doi = abstracts.doi ORDER BY abstracts.embedding <=> %s LIMIT 15',
                                   (embedding,)).fetchall()

            print_results(results)

def start():
    model = INSTRUCTOR('hkunlp/instructor-xl')
    print()
    with psycopg.connect("dbname=arxiv") as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            loop(model, cur)

if __name__ == '__main__':
    start()
