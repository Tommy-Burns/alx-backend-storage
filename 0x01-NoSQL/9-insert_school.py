#!/usr/bin/env python3
"""Using the pymongo module"""


def insert_school(mongo_collection, **kwargs):
    """insert a document into mongo_collection"""
    doc = mongo_collection.insert_one(kwargs)
    return doc.inserted_id
