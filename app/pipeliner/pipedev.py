# For tuning and pickling pipelines
# By Charles Landau

from sklearn.externals import joblib
from sklearn.datasets import fetch_20newsgroups
from sklearn.model_selection import GridSearchCV
from time import time
import json
import os


class TextPipliner:
    """A tool for developing new pickled Pipelines for use in the
    Text Pipeliner webapp."""

    def __init__(self, name, pickle_registry=None,
                 pipeline=None, search_params=None,
                 news_categories=None):
        self.name = name
        self._pickle_registry = pickle_registry
        self._pipeline = pipeline
        self._search_params = search_params
        self._categories = news_categories
        self.score = None

    # Getters and setters
    def get_pickle_registry(self):
        """Return the pickle registry"""
        return self._pickle_registry

    def get_pipeline(self):
        """Return the pipeline"""
        return self._pipeline

    def get_search_params(self):
        """Return the GridSearchCV params"""
        return self._search_params

    def get_categories(self):
        """Return the newsgroup categories"""
        return self._categories

    def set_pipeline(self, pipeline):
        """Set the pipeline."""
        self._pipeline = pipeline

    def set_search_params(self, search_params):
        """Return the GridSearchCV params. No typechecks."""
        self._search_params = search_params

    def set_categories(self, categories):
        """Return the newsgroup categories"""
        self._categories = categories

    # Run the pipeline
    def run(self, persist=True, persist_dir='./', verbose=False):

        # Validate filepath before we do anything expensive
        if persist:
            if not os.path.isdir(persist_dir):
                raise NotADirectoryError(
                    "{} is not a valid directory!".format(persist_dir))

        # Notify about downloads accurately
        if verbose:
            if self._categories:
                print("Loading 20 newsgroups dataset for categories:")
                print(self._categories)
            else:
                print(
                    "Loading 20 newsgroups dataset for all categories..."
                    "this could take a bit.")

        # Fetch. We don't need the corpus as a data member.
        data = fetch_20newsgroups(subset='train', categories=self._categories)
        self._categories = data.target_names
        if verbose:
            print("%d documents" % len(data.filenames))
            print("%d categories" % len(data.target_names))

        # Construct the pipeline object, raise if we haven't already.
        if self._pipeline:
            grid_search = GridSearchCV(
                estimator=self._pipeline, **self._search_params)
        else:
            raise ValueError("Missing pipeline, use .set_pipeline()")

        # Validate filepath before we get to the expensive stuff
        if persist:
            try:
                assert os.path.isdir(persist_dir)
            except AssertionError:
                raise NotADirectoryError(
                    "{} is not a valid directory!".format(persist_dir))

        # Tell a developer to be patient
        if verbose:
            print("Performing grid search...")
            t0 = time()
        # Gridsearch can raise its own errors
        grid_search.fit(data.data, data.target)

        if verbose:
            print("done in %0.3fs" % (time() - t0))
            print()

        # Save the score as a data member
        self.score = grid_search.best_score_

        # Persistence
        if persist:
            # Fit the pipeline with the tuned params
            self._pipeline.set_params(
                **grid_search.best_estimator_.get_params())
            self._pipeline.fit(data.data, data.target)

            # Generate path
            self.path = os.path.join(persist_dir, self.name)

            # Pickle the pipeline at path
            joblib.dump(self._pipeline, self.path)

            # Return the fitted search, with path to the pickle
            return grid_search, self.path

        # Terminate without pickling
        return grid_search, None

    def as_registry(self, fp, description, overwrite=True):
        """Express member data as a valid entry for the
        pickle_registry ledger.

        WARNING: will overwrite the file by default.

        TODO: More robust directory handling."""

        # Pickle has to exist...
        try:
            self._pipeline = joblib.load(filename=self.path)
        except Exception as e:
            raise e

        # Express the entry as a dict
        entry = {
            "name": self.name,
            "answer_key": {i: y for i, y in enumerate(self._categories)},
            # Dirty introspection
            "components": [
                name[1].__class__.__name__ for name in self._pipeline.steps
            ],
            "score": self.score,
            "search_params": self._search_params,
            "description": description,
        }

        # Save and return the entry as JSON
        if overwrite:
            with open(fp, 'w') as file:
                json.dump(entry, file)
        else:
            with open(fp, 'a') as file:
                json.dump(entry, file)
        return entry
