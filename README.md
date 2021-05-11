# onenote_to_markdown
Script to convert MS OneNote for Windows 10 notebooks to directories of markdown files. This can be helpful when moving from MS OneNote to Joplin.

# How to use
1. Select and copy all the notes in the OneNote notebooks you would like to convert to markdown files
2. Save each notebook in a single directory as its own text file with the notebook name as the name of the text file
3. Make sure Python 3 is installed on your machine
4. Open command prompt and run `pip install win32_setctime` and `pip install pytz` 
5. run `python converter.py '/path/to/your/text/files'`
6. Onenote notes are now converted to markdown files in the supplied path
7. To import the files to Joplin. Open Joplin and go to File->Import->MD - Markdown Directory and select the directories you would like to import

# Notes
- The modified and created dates of the output markdown files are set as the created date of the OneNote notes
- This script was only tested on Microsoft OneNote for Windows 10 and Python 3.7 
