from project import collect_files, categorize, remove_duplicates

import os


def test_collect_files():

    dirname = os.path.dirname(__file__)
    dir_path = os.path.join(dirname, "test_mp3s")
    meta_data = collect_files(dir_path)

    assert len(meta_data) == 13


def test_remove_duplicates():

    dirname = os.path.dirname(__file__)
    dir_path = os.path.join(dirname, "test_mp3s")
    meta_data = collect_files(dir_path)
    meta_data, duplicate_files = remove_duplicates(meta_data)
    assert len(duplicate_files) == 3


def test_categorize():

    dirname = os.path.dirname(__file__)
    dir_path = os.path.join(dirname, "test_mp3s")
    meta_data = collect_files(dir_path)
    meta_data, duplicate_files = remove_duplicates(meta_data)
    assert len(meta_data) == 10
    sorted_data, folders = categorize(meta_data, "year")
    assert len(folders) == 4
    sorted_data, folders = categorize(meta_data, "artist")
    assert len(folders) == 2
