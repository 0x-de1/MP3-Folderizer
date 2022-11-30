from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from flaskwebgui import FlaskUI

import os
from helpers import (
    error_messege,
    df_to_html,
    write_to_sql,
    read_from_sql,
)

from project import (
    collect_files,
    categorize,
    remove_duplicates,
    save_files,
    delete_duplicates,
    PROPERTIES,
)


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get inputs
        mp3_path = request.form.get("source").strip().strip('"')
        category = request.form.get("category")

        # Check inputs

        if not os.path.exists(mp3_path):
            # return error_messege("Please enter a valid source folder")
            return render_template(
                "index.html", PROPERTIES=PROPERTIES, invalid_path=True
            )
        if not category:
            return error_messege("Please select category")
        elif category not in PROPERTIES:
            return error_messege("Category not recognized")

        # Execute functions
        meta_data = collect_files(mp3_path)
        meta_data, duplicate_files = remove_duplicates(meta_data)
        write_to_sql(duplicate_files, "duplicate_files")
        if len(meta_data) == 0:
            return render_template(
                "index.html",
                no_mp3s=True,
                PROPERTIES=PROPERTIES,
            )
        # save category and number of duplicates
        session["category"] = category
        session["duplicates"] = len(duplicate_files)
        # Write to SQL database
        write_to_sql(meta_data, "meta_data")
        return redirect("/preview")

    return render_template(
        "index.html",
        PROPERTIES=PROPERTIES,
    )


@app.route("/preview", methods=["GET", "POST"])
def preview():

    meta_data = read_from_sql("meta_data")

    if request.method == "POST":

        category = request.form.get("category")

        meta_data, folders = categorize(meta_data, category)
        # Write categorized df to SQL database
        write_to_sql(meta_data, "sorted_df")
        write_to_sql(folders, "folders")
        mp3s_table = df_to_html(meta_data)
        folder_table = df_to_html(folders)
        session["category"] = category

        return render_template(
            "preview.html",
            folder_table=folder_table,
            mp3s_table=mp3s_table,
            PROPERTIES=PROPERTIES,
            selection=category,
        )

    category = session["category"]
    meta_data, folders = categorize(meta_data, category)

    # Write categorized df to SQL database
    write_to_sql(meta_data, "sorted_df")
    write_to_sql(folders, "folders")
    # Generate HTML code
    mp3s_table = df_to_html(meta_data)
    folder_table = df_to_html(folders)
    # Get number of mp3 files found
    count = len(meta_data)
    duplicates = session["duplicates"]
    return render_template(
        "preview.html",
        folder_table=folder_table,
        mp3s_table=mp3s_table,
        PROPERTIES=PROPERTIES,
        selection=category,
        count=count,
        duplicates=duplicates,
    )


@app.route("/save", methods=["GET", "POST"])
def save():

    sorted_df = read_from_sql("sorted_df")
    folders = read_from_sql("folders")

    mp3s_table = df_to_html(sorted_df)
    folder_table = df_to_html(folders)

    if request.method == "POST":
        destination = request.form.get("destination").strip().strip('"')
        method = request.form.get("method")

        if not os.path.exists(destination):
            category = session["category"]
            # Provide invalid path warning
            return render_template(
                "preview.html",
                PROPERTIES=PROPERTIES,
                invalid_path=True,
                mp3s_table=mp3s_table,
                folder_table=folder_table,
                selection=category,
            )
        sorted_df = read_from_sql("sorted_df")
        # duplicate = session["duplicate"]
        if method == "moving":
            duplicate_files = read_from_sql("duplicate_files")
            delete_duplicates(duplicate_files)
        file_errors = save_files(sorted_df, destination, method)
        return render_template(
            "saved.html",
            method=method,
            destination=destination,
            file_errors=file_errors,
            folder_table=folder_table,
            PROPERTIES=PROPERTIES,
        )


@app.route("/help", methods=["GET", "POST"])
def help():

    return render_template("help.html")


if __name__ == "__main__":
    # If you are debugging you can do that in the browser:
    # app.run()
    # If you want to view the flaskwebgui window:
    FlaskUI(app=app, server="flask").run()
