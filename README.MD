# MP3 Folderizer
![title](static/title.jpg "title" )
## Video Demo: https://www.youtube.com/watch?v=mvjOIrduhq8

### Description:MP3 Folderizer is a software that can organize your mp3 library into folders based on Album, Artist, Year, Album artist or Genre

# Installation:

Download the latest release (.exe) file and run or Run app.py file to open the web app and follow the instructions below

# Usage Instructions:
![home](static/home.jpg "home" )

## Step 1: Load MP3 files

Enter your source folder path here. MP3 Folderizer will search all directories in your source folder for mp3 files

## Step 2: Categorize MP3 files

![category](static/category.png "category" )

Select the category you want the mp3 files to be categorized in to folders by. Options include Album, Artist, Album artist, Year and Genre.

## Step 3: Proceed to preview
![mp3list](static/mp3list.png "mp3list" )


Press proceed to preview. You will now see the folder list and the number of mp3 files in each folder.

> - To view full list of mp3 files click on **\*Show/Hide MP3** list button\*
> - To change the category select from drop down and press **_Change category_** button

## Step 4: Create folder structure
![moving](static/moving.png "moving" )

> 1. Enter your destination folder path to create the folder structure
> 2. Select whether mp3 files are to be copied or moved

If moved, all previous files will be removed and moved to the new file structure at the provided destination folder

Press **Proceed** to continue

## Step 5: Summery
![summery](static/summery.png "summery" )

View all the errors detected during thew operation and folder structure created

# Project Files/Folders:

<kbd>static</kbd>: Contains all static files required for the flask web app

<kbd>templates</kbd>: Contains all html files of the web app

> - **index.html:** Collects inputs for source folder and category
> - **preview.html:**
>   - **Change category section:** previews folder structure, Sorted mp3 list. Gives option to re-structure the folders.
>   - **Create folder structure section:** Collects inputs for destination folder and file transfer method move or copy
> - **help.html:** App usage guide.
> - **layout.html:** Contains basic html layout.
> - **saved.html:** Shows if operation is success full and errors occured during operation and final folder structure.
> - **error_messege.html:** Shows error messege if invalid inputs are given.

<kbd>test_mp3s</kbd>: Contains mp3 files for pytest

<kbd>app.py</kbd>: Contains the routes for the flask web gui app. Acts like a main function.
<kbd>project.py</kbd>: Contains all the main funtions for the program

> - **collect_files(mp3_path):** Collects all mp3 files inside the mp3_path using os.walk, then scans for mp3 tags of those files and writes them to a pandas dataframe. Errors and previous folder paths are written to files in /static/data
> - **categorize(meta_data, method):** Adds foldert column to the dataframe accrding to the method provided and sorts the dataframe so that biggest folder comes first
> - **save_files(df, save_path, method):** Gets sorted dataframe, destination folder path and file transfe method as inputs and creates the folder structure copies or moves the mp3 files to it's respective folder .
> - **remove_duplicates(meta_data):** Gets sorted dataframe as input and returns dataframe of duplicate files and sorted dataframe without duplicate files.

<kbd>test_project.py</kbd>: Contains pytests for collect_files, remove_duplicates and categorize

<kbd>data.db</kbd>: stores data frames as tables for the flask web app
