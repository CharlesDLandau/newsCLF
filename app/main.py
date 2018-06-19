from flask import Flask, render_template, request, Markup, abort
import json
import markdown
from pipeliner import handlers as hd
from pipeliner import registry as rg
import warnings
warnings.simplefilter("ignore", UserWarning)


# The pickles are available on startup
reg = rg.PickleRegister("./pipeliner/register.json",
                        "./pipeliner/store/")
pickle_store = reg.load_pickles()

# The API handler functions are available.
ap = hd.APIHandler(reg, pickle_store)

# Flask is available.
app = Flask(__name__)


# The homepage
@app.route("/")
def index():
    with open("./templates/demo.md", "r") as markfile:
        content = Markup(markdown.markdown(markfile.read()))
    return render_template('index.html', **locals())


# The API documentation
@app.route("/api/docs")
def api_docs():
    with open("./templates/apidocs.md", "r") as markfile:
        content = Markup(markdown.markdown(markfile.read()))
    return render_template("index.html", **locals())


@app.route("/about")
def aboutpage():
    with open("./templates/about.md", "r") as markfile:
        content = Markup(markdown.markdown(markfile.read()))
    return render_template("index.html", **locals())


# The do-it-yourself page.
@app.route("/diy")
def diy():
    pickles = pickle_store.keys()
    return render_template('index.html', **locals())


@app.route('/diy/submission', methods=['POST'])
def form_post():
    formID, prediction, diy_ttr_value, description = ap.form_renderer(
        request.form)
    return render_template('index.html', **locals())


@app.route('/api/pickleregister', methods=['GET'])
def get_register():

    # Handle with no id param
    if not request.args.get("id"):
        resp = json.dumps(ap.register)

    else:
        # Bad request
        if request.args.get("id") not in reg._ids["all"]:
            abort(400)
        # Handle with valid id
        entry = ap.register["register"][request.args.get("id")]
        resp = {"register": entry}
    return hd.GetRegister(json.dumps(resp)), 201


@app.route('/api/predict', methods=['POST'])
def post_prediction():

    # Request is JSON
    if not request.json:
        abort(400)

    # Bad request
    if request.json["id"] not in reg._ids["all"]:
        abort(400)

    # Access the pickle
    model = pickle_store[request.json["id"]]
    try:
        prediction = model.predict([request.json["text"]])[0]
    except Exception:
        abort(400)

    # Form the response
    resp = {}
    entry = ap.register["register"][request.json["id"]]
    prediction = entry["payload"]["answer_key"][str(prediction)]
    resp["prediction"] = prediction
    resp["register"] = entry

    return hd.GetPrediction(json.dumps(resp)), 201


# Run on debug mode
if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=80)
