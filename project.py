# Grab meta data for a given mp3s and save to a csv
import os
import eyed3
import json
from datetime import datetime
import csv
import pandas as pd
import shutil
import sys

PROPERTIES = ["album", "artist", "album_artist", "year", "genre"]


def main():
    # Get source folder
    mp3_path = get_path("Enter mp3 source folder: ")

    # Scan for mp3 files in the source folder
    meta_data = collect_files(mp3_path)

    # Get mp3 file count
    file_count = len(meta_data)

    # Exit the program if no mp3s present in the folder
    if file_count == 0:
        print(f"No mp3 files in {mp3_path}")
        sys.exit()
    print(f"{file_count} files collected!")

    # Remove duplicates and get list of duplicate files
    meta_data, duplicate_files = remove_duplicates(meta_data)

    # Get category to sort folders by
    method = get_property(f"Categorize mp3 files to folders by: {PROPERTIES}: ")

    # Categorize the mp3s to folders and get sorted dataframe and folder list
    sorted_data, folders = categorize(meta_data, method)

    # Iterate until user is satisfied with the folder structure
    while True:
        print_folders(sorted_data)
        answer = (
            input("Do you want to proceed with this folder structure? (Y/N)")
            .strip()
            .upper()
        )
        if answer == "Y":
            break
        elif answer == "N":
            method = get_property(
                f"Categorize the mp3 files to folders by: {PROPERTIES}: "
            )
            sorted_data, folders = categorize(meta_data, method)
        else:
            print("Enter a valid response")
    # Get destination
    destination = get_path("Enter destination to create the folder structure: ")

    # Get confirmation to move files
    if confirm_move():
        delete_duplicates(duplicate_files)
        errors = save_files(sorted_data, destination, "moving")
    else:
        errors = save_files(sorted_data, destination, "copying")

    print("Operation completed!")
    if errors:
        print("Error list")
        print(errors)


def get_path(prompt):
    while True:
        path = input(prompt).strip().strip('"')
        if os.path.exists(path):
            return path
        else:
            print("invalid folder path")


def confirm_move():
    # Give option to copy or move
    while True:
        confirm = (
            input("Do you want to create a copy or to move? (COPY / MOVE): ")
            .upper()
            .strip()
        )
        if confirm == "MOVE":
            re_confirm = (
                input(
                    "All previous files will be removed. Do you want to proceed? (Y/N): "
                )
                .upper()
                .strip()
            )
            if re_confirm == "Y":
                return True
            else:
                continue
        elif confirm == "COPY":
            return False
        else:
            continue


def get_property(prompt):
    while True:
        property = input(prompt).strip().lower()
        if property in PROPERTIES:
            return property
        else:
            print("Enter a valid response")
            continue


def remove_duplicates(df):
    # Collect duplicate files
    duplicate_files = df[df.duplicated(subset=["file name", "file size"])]
    # Remove duplicates
    df = df.drop_duplicates(subset=["file name", "file size"]).reset_index(drop=True)

    return df, duplicate_files


def delete_duplicates(df):
    # List comprehension to iterate through the dataframe
    [os.remove(cur_path) for cur_path in df.path]


def collect_files(mp3_path):
    def get_metadata(all_files: list):
        meta_data = []
        errors = []

        # Process year from mp3 tag
        def get_year(date):
            date = str(date)
            if date == "None":
                date = None
            elif len(date.strip()) > 4:
                date = datetime.fromisoformat(date).year
            return date

        # Process genre from mp3 tag
        def get_genre(genre):
            genre = str(genre)
            if genre == "None":
                genre = None
            else:
                genre = genre.strip("()1234567890 ")
            return genre

        # Process any tag from mp3 tag
        def get_attribute(attribute):
            attribute = str(attribute).strip()
            if attribute in ["None", ""]:
                attribute = None

            return attribute

        for folder in all_files:
            for mp3 in folder["files"]:
                try:
                    # initiate audio file
                    audiofile = eyed3.core.load(mp3)
                    if not audiofile:
                        errors.append({"error name": "Could not load", "file": mp3})
                        continue
                    tag = audiofile.tag
                    if not tag:
                        # errors.append({"error name": "No mp3 tag available", "file": mp3})
                        dict = {
                            "file name": os.path.basename(mp3),
                            "title": None,
                            "album": None,
                            "artist": None,
                            "album_artist": None,
                            "genre": None,
                            "year": None,
                            "file size": os.stat(mp3).st_size,
                            "modified time": datetime.fromtimestamp(
                                os.stat(mp3).st_mtime
                            ),
                            "length": audiofile.info.time_secs,
                            "directory": folder["root"],
                            "path": mp3,
                        }
                        meta_data.append(dict)
                        continue
                    # get tag data
                    # file name,file size,modified time,subfolder,path, title, date, duration, album, artist,album_artist,  track number
                    dict = {
                        "file name": os.path.basename(mp3),
                        "title": get_attribute(tag.title),
                        "album": get_attribute(tag.album),
                        "artist": get_attribute(tag.artist),
                        "album_artist": get_attribute(tag.album_artist),
                        "genre": get_genre(tag.genre),
                        "year": get_year(tag.getBestDate()),
                        "file size": os.stat(mp3).st_size,
                        "modified time": datetime.fromtimestamp(os.stat(mp3).st_mtime),
                        "length": audiofile.info.time_secs,
                        "directory": folder["root"],
                        "path": mp3,
                        # "track number": tag.track_num,
                    }
                    meta_data.append(dict)
                    # yield dict
                except AttributeError as e:
                    errors.append({"error name": e, "file": mp3})

        return meta_data, errors

    def get_mp3s(mp3_path):

        # get all mp3 files and directories to a list of dicts
        all_files = []
        for root, dirs, files in os.walk(mp3_path, topdown=True):
            for file in files:
                # detect if this folder contains any mp3 files
                # .lower is used to capture capital MP3 files also
                if file.lower().endswith(".mp3"):
                    # if yes collect all mp3s in folder to the below dict structure
                    dict = {
                        "root": root,
                        "files": [
                            os.path.join(root, mp3.lower())
                            for mp3 in files
                            if mp3.lower().endswith(".mp3")
                        ],
                    }
                    all_files.append(dict)
                    break
        return all_files

    def save_data(all_files, errors):
        # record existing tree structure
        # get current date time
        today = datetime.now().strftime("%Y%m%d_%H%M%S")

        # generate dirs path
        dirname = os.path.dirname(__file__)
        dirs_path = os.path.join(dirname, f"static//data//dirs_{today}")

        # save existing file tree to a json for recovery
        with open(dirs_path, "w") as fout:
            json.dump(all_files, fout)
        # generate errors path
        error_path = os.path.join(dirname, f"static//data//errors_{today}.csv")
        with open(error_path, "w", encoding="utf-8", newline="") as csvfile:
            fieldnames = ["error name", "file"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for error in errors:
                writer.writerow(error)

    # search for all files in given directory
    all_files = get_mp3s(mp3_path)
    # Check if directory contains mp3s
    if len(all_files) == 0:
        print("No mp3 files in the folder")
    # get metadata and write to a csv
    # name, title, date, duration, file size, album, artist, subfolder, track number
    meta_data, errors = get_metadata(all_files)

    # saves initial directories and errors of files
    save_data(all_files, errors)
    # Return data as a dataframe
    df = pd.DataFrame(meta_data)
    return df


# Categorize to folders
def categorize(df, category):

    # Categorize folders by value counts of category
    df["temp"] = df.loc[:, category].map(df.loc[:, category].value_counts())
    # Here metadata["artist"].value_counts() returns a series. A pandas series can be interprited as a dictionary.
    # In map function if the dictionaries key is in the column it gets replaced by the value of the key.

    # sort df so that biggest folder comes first & remove the temp column
    df = (
        df.sort_values(by=["temp", category, "title", "file name"], ascending=False)
        .reset_index(drop=True)
        .drop("temp", axis=1)
    )

    # set category as "folder" to the first column
    df.insert(0, "folder", "")
    # convert folder to string to avoid future conflicts
    df[category] = df[category].dropna().astype(str)

    # Get categories with atleast 2 songs as folders
    folders = df[category].value_counts()
    folders = folders[folders.values > 1].index

    # Assign folder names for folders
    df["folder"] = df[category].apply(lambda x: x if x in folders else "Uncategorized")

    folders = preview_folders(df)
    return df, folders


def print_folders(df):
    # Show folder structure summery because you can't show the whole df
    folders = df.folder.value_counts()
    # Give the option to the user to view the folder structure as an excel file

    heading = "Folder name : No. of mp3s"
    print(f"{heading :<60}{heading :<60}{heading} ")
    print()
    for i in range(0, len(list(folders)), 3):

        if len(list(folders)) >= i + 3:
            col_1 = f"{i+1}. {folders.index[i]} : {folders.values[i]}"
            col_2 = f"{i+2}. {folders.index[i+1]} : {folders.values[i+1]}"
            col_3 = f"{i+3}. {folders.index[i+2]} : {folders.values[i+2]}"
            print(f"{col_1:<60}  {col_2:<60}  {col_3}")

        elif len(list(folders)) == i + 2:
            col_1 = f"{i+1}. {folders.index[i]} : {folders.values[i]}"
            col_2 = f"{i+2}. {folders.index[i+1]} : {folders.values[i+1]}"
            print(f"{col_1:<60}  {col_2}")

        else:
            col_1 = f"{i+1}. {folders.index[i]} : {folders.values[i]}"
            print(f"{col_1}")


def preview_folders(df):
    # Show folder structure summery because you can't show the whole df
    # get folder value counts
    folders = df.folder.value_counts()
    # convert to dataframe since series cannot be converted to html
    folders = pd.DataFrame(folders).reset_index()
    # change column names
    folders.columns = ["Folder name", "No. of mp3s"]

    return folders


def save_files(df, save_path, method):
    def create_folders(df, save_path):
        # Remove un-usable symbols from folder name category \ / : * ? " < > |
        df["temp"] = df.iloc[:, 0].dropna().apply(symbol_remover)
        df.iloc[:, 0] = df["temp"]
        df = df.drop("temp", axis=1)

        # load folder names from first column
        folders = df.iloc[:, 0].value_counts()
        folders = folders[folders.values > 1]
        folders = folders.index

        errors = []
        for folder in folders:
            try:
                folder_path = os.path.join(save_path, folder)
                os.mkdir(folder_path)
            except FileExistsError:
                # errors collects all the folder names with conflicting capitalization
                errors.append(["Folder already exists", folder])

        return df, errors

    def move_mp3s(df, save_path, errors):

        # If category has atleast 2 songs add it to folders
        folders = df.folder.value_counts()
        folders = list(folders[folders.values > 1].index)

        # Iterate through dataframe where folder true
        def move_to_folder(folder, cur_path, save_path):
            file = os.path.basename(cur_path)
            # if song does not belong to a folder (NaN which is representeed by float)
            if isinstance(folder, (float, bool)):
                # create destination path
                new_path = os.path.join(save_path, "Uncategorized", file)
            else:
                # create destination path
                new_path = os.path.join(save_path, folder, file)
            try:
                # copy song to new_path
                shutil.move(cur_path, new_path)
                # print(cur_path, new_path)
            except (FileNotFoundError):
                errors.append(["File not Found at", cur_path])
            except (shutil.SameFileError):
                errors.append(["Source and destination same location", cur_path])

        # List comprehension to iterate through the dataframe
        [
            move_to_folder(folder, cur_path, save_path)
            for folder, cur_path in zip(df.folder, df.path)
        ]

        # delete previous folders (only deletes empty folders)
        mp3_folders = list(df.directory.unique())

        for folder_path in sorted(mp3_folders, reverse=True):
            try:
                os.rmdir(folder_path)
            except FileNotFoundError:
                errors.append(["Folder not found", folder_path])

            except OSError:
                errors.append(["Previous folder not deleted", folder_path])
        return errors

    def copy_mp3s(df, save_path, errors):
        # If category has atleast 2 songs add it to folders
        folders = df.folder.value_counts()
        folders = list(folders[folders.values > 1].index)

        # Iterate through dataframe where folder true
        def copy_to_folder(folder, cur_path, save_path):
            # Extract file name
            file = os.path.basename(cur_path)
            # if song does not belong to a folder (NaN which is representeed by float)
            if isinstance(folder, (float, bool)):
                # create destination path
                new_path = os.path.join(save_path, "Uncategorized", file)
            else:
                # create destination path
                new_path = os.path.join(save_path, folder, file)
            try:
                # copy song to new_path
                shutil.copy2(cur_path, new_path)
                # print(cur_path, new_path)
            except (FileNotFoundError):
                errors.append(["File not Found at", cur_path])
            except (shutil.SameFileError):
                errors.append(["Source and destination same location", cur_path])

        # List comprehension to iterate through the dataframe
        [
            copy_to_folder(folder, cur_path, save_path)
            for folder, cur_path in zip(df.folder, df.path)
        ]

        return errors

    def symbol_remover(text):
        x = '\/:*?"<>|'
        y = "         "

        mapping_table = text.maketrans(x, y)
        return text.translate(mapping_table)

    # Create folders and get updated df
    df, errors = create_folders(df, save_path)

    # Get confirmation to move files
    if method == "moving":
        errors = move_mp3s(df, save_path, errors)
    elif method == "copying":
        errors = copy_mp3s(df, save_path, errors)
    if len(errors) > 0:
        return errors


if __name__ == "__main__":
    main()
