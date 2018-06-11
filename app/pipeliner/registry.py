# Manage the pickles
from flask import Response
import os
import json
from sklearn.externals import joblib


class PickleRegister:
    """A JSON array. Accepts a relpath to the register.json file
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

        # An empty JSON array.
        if new_register:
            with open(path, 'w') as w:
                json.dump([], w)

        with open(path, 'r') as f:
            register = json.load(f)

        # The register is a JSON array.
        if not type(register) == list:
            raise ValueError("Invalid register file.")

        self._pickletypes = set([j["pickletype"] for j in register])
        if len(self._pickletypes) == 1:
            # Duplicative and dirty, but cheap. Keeps the interface clean.
            self._ids = {
                "all": [i["id"] for i in register],
                list(self._pickletypes)[0]: [
                    i["id"] for i in register]
            }
        else:
            self._ids = {"all": [i["id"] for i in register]}
            # Searchable by pickletype
            for label in self._pickletypes:
                self._ids[label] = [
                    i["id"] for i in register if i["pickletype"] == label]

        # Finally assign the _register
        self._register = register

    def new_entry(self, entry, pickletype, id=None):
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
        if not id:
            id = entry["name"]

        # Check if id already exists.
        for i in self._ids["all"]:
            if i == id:
                raise ValueError(
                    "{} is already registered, did you"
                    " mean to use update_entry()?".format(id))

        # Affix the metadata
        entry = {"id": id, "pickletype": pickletype, "payload": entry}

        # Append to the members
        self._register.append(entry)
        self._ids["all"].append(id)
        # In case a new pickletype
        if pickletype not in self._ids.keys():
            self._ids[pickletype] = []
            self._pickletypes.update([pickletype])
        self._ids[pickletype].append(id)

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
        for ent in self._register:
            if ent["id"] == entry["id"]:
                ent = entry

        with open(self.path, 'w') as f:
            json.dump(self._register, f)

        return None

    def delete_entry(self, id, raise_notfound=False):
        # Find and delete an entry.

        if raise_notfound:
            # Register is a list, so this should get discrete entries O(1)
            size = len(self._register)
        # Filter it out
        register = [x for x in self._register if x["id"] != id]

        # Panic condition, this should never happen since ids are unique
        assert not size - 1 > len(register)

        if raise_notfound:
            try:
                assert size - 1 == len(register)
            except AssertionError:
                raise ValueError("""ID "{}" not found.""".format(id))

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
            pickle_set = [i["id"] for i in self._register]

        # Generate a dict of {id: loaded pickle, ...} pairs.
        pickle_map = {
            id: joblib.load(
                os.path.join(self.storepath, id)) for id in pickle_set
        }

        # Return the dict - pickles are loaded into memory and accessible.
        return pickle_map

