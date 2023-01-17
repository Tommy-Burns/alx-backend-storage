#!/usr/bin/env python3
"""Using the Pymongo module"""


def list_all(mongo_collection):
    """list all documents in mongo_collection"""
    col_documents = mongo_collection.find({})
    return col_documents
