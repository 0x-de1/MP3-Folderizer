import os

from flask import render_template
import pandas as pd
from sqlite3 import connect


def df_to_html(meta_data):
    meta_data.index += 1
    meta_data.columns = meta_data.columns.str.capitalize()
    html_code = [
        meta_data.to_html(
            classes="table table-light table-striped table-hover text-start",
            header="true",
            show_dimensions=True,
        )
    ]
    html_code[0] = html_code[0].replace(
        '<tr style="text-align: right;">', '<tr style="text-align: left;">'
    )
    return html_code


def error_messege(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("error_messege.html", top=code, bottom=escape(message)), code


# write to sql data base
def write_to_sql(meta_data, table_name):

    conn = connect("data.db", check_same_thread=False)
    meta_data.to_sql(
        table_name,
        conn,
        if_exists="replace",
        index=False,
    )
    conn.commit()
    conn.close()


def read_from_sql(table_name):
    conn = connect("data.db", check_same_thread=False)
    sql_query = f"SELECT * FROM {table_name}"
    meta_data = pd.read_sql(
        sql_query,
        conn,
    )
    return meta_data


def sorted_df_from_sql():
    conn = connect("data.db", check_same_thread=False)
    meta_data = pd.read_sql(
        "SELECT * FROM sorted_df",
        conn,
    )
    return meta_data
