# Feature Extraction Pipelines

Feature selection is one of the toughest parts of machine learning -- oftentimes we're working in extremely high-dimensional space (as in the case of working with text data), and it's very difficult to identify and extract the features that will be most informative to a predictive model.

Grid search techniques can help us to find the best combination of features, but in a software engineering context, we also need a robust and repeatable means of integrating normalization, transformation, vectorization, feature union, and modeling into a single process -- thankfully the Scikit-Learn `Pipeline` object gives us just that!

# Classifying News Articles using a Feature Extraction Pipeline
The [Scikit-Learn documentation](http://scikit-learn.org/stable/auto_examples/model_selection/grid_search_text_feature_extraction.html) gives a good procedural illustration of how you can use pipelines for feature extraction on a text data classification problem.

But... what if we wanted to put something like this into production?

## Delivery model
To serve a pipeline like this in production, it needs to be delivered like a production service.

![Delivery of Text Pipeliner](static/text_pipelining.jpg)

Text Pipeliner uses Docker for containers and Flask to create web applications. Docker images are generated in the development environment and pushed into production, where they make the Flask app available. Well formed requests from Text Pipeliner's web interface and RESTful API come in, and responses come out, as with any other service. With this delivery model, Text Pipeliner can be used in conjunction with an API gateway to realize some of the horizontal scaling benefits associated with a microservices architecture.

## Interface
To productionize pipelines, Text Pipeliner implements the `pipeliner` package with classes for development (`pipedev`), registration of pipelines for use in the app (`registry`), and for implementing the API (`handlers`).

![Behaviors and Interfaces Across Environments: pipeliner](static/interface.jpg)

In this way, the `pipeliner` package provides a developer interface for delivering models to production, as well as a means of consuming the models in response to API queries.


## A note about "production"...
Text Pipeliner demonstrates how a `pipeline` can be productionized, but don't make the mistake of thinking that the Flask application is production-ready! There's plenty left to do before that can happen, such as:

* Securing the application
* Rate limiting
* Authentication
* Build the test suite
* WSGI configuration