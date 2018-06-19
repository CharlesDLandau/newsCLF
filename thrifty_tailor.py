# Import pipeliner modules:
import app.pipeliner.pipedev as piper
import app.pipeliner.registry as rg

# sklearn imports:
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import SGDClassifier
import warnings
import os
warnings.simplefilter("ignore", FutureWarning)


if not os.path.isdir("./app/pipeliner/store"):
    os.mkdir("./app/pipeliner/store")

if __name__ == '__main__':
    # Construct a new project and give it a name (id)
    tp = piper.TextPipliner("pickle0003")

    # Set the estimator
    tp.set_pipeline(Pipeline([
        ('vect', CountVectorizer()),
        ('tfidf', TfidfTransformer()),
        ('clf', SGDClassifier()),
    ]))

    # Set the categories (skipping this runs on all newsgroups)
    tp.set_categories([
        'alt.atheism',
        'talk.religion.misc',
    ])

    # Set arguments for GridSearch (including the parameter space to search)
    tp.set_search_params({
        "verbose": 1,
        "n_jobs": -1,
        "param_grid": {
            'vect__max_df': (0.5, 0.75, 1.0),
            'vect__max_features': (None, 5000, 10000, 50000),
            #'vect__ngram_range': ((1, 1), (1, 2)),  # unigrams or bigrams
            #'tfidf__use_idf': (True, False),
            'tfidf__norm': ('l1', 'l2'),
            'clf__alpha': (0.00001, 0.000001),
            #'clf__penalty': ('l2', 'elasticnet'),
            #'clf__n_iter': (10, 50, 80),
        }})

    # Tune and persist the pipeline
    # You may need to:
    # 1: Run this line in a __main__ protected block
    # 2: Create the /store folder as it is excluded in the .gitignore
    # 3: Or, run thrifty_tailor.py from a venv built out of requirements.txt
    # 4: (It tries to fit a cheap model)
    tp.run(persist_dir="./app/pipeliner/store/")

    # Write a new PickleRegister at "./app/pipeliner/register.json"
    # The pickles are being persisted to "./app/pipeliner/store/"
    reg = rg.PickleRegister("./app/pipeliner/register.json",
                            "./app/pipeliner/store/", new_register=True)

    # The TextPipeliner as_registry() method takes a filepath to persist the metadata
    # and a description of the pickle. It returns a valid argument for the PickleRegister
    # new_entry() method.
    item = tp.as_registry("./app/pipeliner/store/pickle0003.json", "A"
                          " pipeline tuned on a broad parameter space, "
                          "trained on two categories in the newsgroup20 corpus.")

    # new_entry() also expects a pickle_type ("pipeline" in this case)
    reg.new_entry(item, "pipeline")

    # You may also want to ensure that all pickles load properly...
    # main.py uses the load_pickles() method on startup to construct the pickle store.
    pickle_store = reg.load_pickles()
