# Manage the pickles
import os
import json
from sklearn.externals import joblib


class PickleRegister:
    """A JSON object. Accepts a relpath to the register.json file
    and to the pickles themselves.
    Supports pickletype so we can add new kinds of pickles later.
    The load_pickles method is used to load all the registered pickles
    into memory and mapping them to a dict by id.

    Call signature:
    PickleRegister("path/to/register.json", path/to/picklestore/")"""
    __slots__ = "path", "storepath", "_ids", "_pickletypes", "_register"

    def __init__(self, path, storepath, new_register=False):
        self.path = path
        self.storepath = storepath

        # An empty JSON object.
        if new_register:
            with open(path, 'w') as w:
                json.dump({"register": {}}, w)

        with open(path, 'r') as f:
            register = json.load(f)

        # The register is a JSON object.
        if not isinstance(register, dict):
            raise ValueError("Invalid register file.")

        # For iterating through the register to generate values
        itr_reg = register["register"].items()

        # Safely assign _pickletypes
        if new_register:
            self._pickletypes = set()
        else:
            self._pickletypes = set(
                [j["pickletype"] for k, j in itr_reg])

        # If empty...
        if len(self._pickletypes) == 0:
            self._ids = {"all": []}

        # If just one registered...
        elif len(self._pickletypes) == 1:
            # Duplicative and dirty, but cheap. Keeps the interface clean.
            self._ids = {
                "all": [i for i, n in itr_reg],
                list(self._pickletypes)[0]: [
                    i for i, n in itr_reg]
            }

        # If longer...
        elif len(self._pickletypes) > 1:
            self._ids = {"all": [i for i, n in itr_reg]}
            # Searchable by pickletype
            for label in self._pickletypes:
                self._ids[label] = [
                    register["register"
                             ][i]["id"] for i, n in itr_reg if n[
                        "pickletype"] == label]  # Bad linting?

        # Finally assign the _register
        self._register = register

    def new_entry(self, entry, pickletype, ID=None):
        # Accepts a new JSON object and registers it

        # Is the entry arg a filepath or dict?
        entry_type = type(entry)
        if entry_type == str:
            with open(entry, 'rb') as f:
                entry = json.load(f)
        elif entry_type == dict:
            pass
        else:
            raise ValueError(
                "Expected filepath or dict, got {}.".format(entry_type))

        # If no id is passed, use the name.
        if not ID:
            ID = entry["name"]

        # Check if id already exists.
        for i in self._ids["all"]:
            if i == ID:
                raise ValueError(
                    "{} is already registered, did you"
                    " mean to use update_entry()?".format(ID))

        # Affix the metadata
        entry = {"id": ID, "pickletype": pickletype, "payload": entry}

        # Append to the members
        self._register["register"][ID] = entry
        self._ids["all"].append(ID)
        # In case a new pickletype
        if pickletype not in self._ids.keys():
            self._ids[pickletype] = []
            self._pickletypes.update([pickletype])
        self._ids[pickletype].append(ID)

        with open(self.path, 'w') as f:
            json.dump(self._register, f)

        return None

    def update_entry(self, entry):
        # Accepts a JSON object and updates the register with it

        # Is the entry arg a filepath or dict?
        entry_type = type(entry)
        if entry_type == str:
            with open(entry, 'rb') as f:
                entry = json.load(f)
        elif entry_type == dict:
            pass
        else:
            raise ValueError(
                "Expected filepath or dict, got {}.".format(entry_type))

        # The id must be registered already.
        if entry["id"] not in self._ids["all"]:
            raise ValueError(
                """Couldn't find the ID "{}" in the register.""".format(
                    entry["id"]))

        # Find and update the entry
        for ent in self._register["register"].keys():
            if ent == entry["id"]:
                self._register["register"][ent] = entry

        with open(self.path, 'w') as f:
            json.dump(self._register, f)

        return None

    def delete_entry(self, ID, raise_notfound=False):
        # Find and delete an entry.

        if raise_notfound:
            # Register is a list, so this should get discrete entries O(1)
            size = len(self._register["register"])
        # Filter it out
        self._ids["all"] = [x for x in self._ids["all"] if x != ID]
        t = self._register["register"][ID]["pickletype"]
        self._ids[t] = [x for x in self._ids[t] if x != ID]
        if len(self._ids[t]) == 0:
            del self._ids[t]
            self._pickletypes = set([x for x in self._pickletypes if x != t])
        self._register = {"register": {
            x: y for x, y in self._register["register"].items() if x != ID}
        }

        # Panic condition, this should never happen since ids are unique
        if raise_notfound and size - 1 > len(register):
            raise Exception(
                "This operation corrupted the register"
                "...exiting to preserve it")

        if raise_notfound and (size - 1) == len(register):
            raise ValueError("""ID "{}" not found.""".format(ID))

        with open(self.path, 'w') as f:
            json.dump(self._register, f)

        return None

    def load_pickles(self, id_subset=False):
        """Load all the pickles using the ids as filenames and return a dict
        to call them with. If the ids do not match the filenames, id_subset
        can feed a predefined list of filenames (not recommended.)"""

        # List of filenames
        if id_subset:
            # Check iterable
            try:
                item_in_iter = iter(id_subset)
            except TypeError:
                raise TypeError("id_subset isn't iterable.")
            # Accept the user input
            pickle_set = id_subset
        else:
            pickle_set = [i for i, k in self._register["register"].items()]

        # Generate a dict of {id: loaded pickle, ...} pairs.
        pickle_map = {
            ID: joblib.load(
                os.path.join(self.storepath, ID)) for ID in pickle_set
        }

        # Return the dict - pickles are loaded into memory and accessible.
        return pickle_map
