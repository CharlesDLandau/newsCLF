# Map the class public interface to API
from flask import Response


class APIHandler():
    """The API handler for Text Pipeliner."""

    def __init__(self, register, pickle_store):
        self.register = register._register
        self.picklestore = pickle_store

    def form_renderer(self, form):
        # Reder the DIY form
        formID = form["pickles"]
        ttr = form["article_text"]
        model = self.picklestore[formID]

        prediction = model.predict([form["article_text"]])[0]

        regObject = self.register["register"][formID]

        description = regObject['payload']['description']

        # Dirty update for the prediction, lookup is cheap.
        prediction = regObject['payload']['answer_key'][str(prediction)]

        if len(ttr) > 100:
            ttr = ttr[:100] + "..."

        return formID, prediction, ttr, description


# Abstract data types
# Inherits Flask Response object so that responses will be customizable
class GetRegister(Response):
    """Response to API request: GetRegister"""

    def __init__(self, response, **kwargs):
        kwargs['mimetype'] = 'application/json'

        super(GetRegister, self).__init__(response, **kwargs)


class GetPrediction(Response):
    """Response to API request: GetPrediction"""

    def __init__(self, response, **kwargs):
        kwargs['mimetype'] = 'application/json'

        super(GetPrediction, self).__init__(response, **kwargs)
