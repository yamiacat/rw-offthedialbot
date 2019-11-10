"""Holds the database handler to work with mongodb."""
import mongomock as pymongo


class DatabaseHandler:
    """Database handler."""

    empty_profile = {
        "status": {
            "IGN": None,
            "SW": None,
            "Ranks": {
                "Splat Zones": None,
                "Rainmaker": None,
                "Tower Control": None,
                "Clam Blitz": None,
            },
        },
        "style_points": [0, 0, 0],  # Groups A, B, and C.
        "competitive_exp": 0,
        "meta": {
            "competing": False,
        },
        "elo": {
            "base": 1000,
            "tournament_exp": 0,
        }
    }

    def __init__(self):
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.client["offthedialbot"]

        # Collections
        self.profiles = self.db["profiles"]

    def create_mock_data(self):
        """Create mock data to test on."""
        profile = self.empty_profile.copy()
        profile["status"]["IGN"] = "LeptoSpira"
        profile["status"]["SW"] = 123412341342
        profile["status"]["Ranks"]["Clam Blitz"] = "S"
        profile["status"]["Ranks"]["Splat Zones"] = "S"
        profile["status"]["Ranks"]["Rainmaker"] = "S"
        profile["status"]["Ranks"]["Tower Control"] = "S"
        profile["_id"] = 571494333090496514
        return self.profiles.insert_one(profile)

    def find_profile(self, id):
        """Find a document in the profiles collection by id."""
        return self.profiles.find_one({"_id": id})

    def new_profile(self, profile, id):
        """Insert a new profile into the profiles collection with id."""
        profile["_id"] = id
        return self.profiles.insert_one(profile)

    def edit_profile(self, profile, id):
        """Update an existing profile in the profiles collection by id."""
        profile["_id"] = id
        return self.profiles.update_one(profile)
