# Bash script to ingest data
# This involves scraping the data from the web and then cleaning up and putting in Weaviate.
# Error if any command fails
set -eu
# wget -r -A.html https://devguide.python.org/

wget -r -l 1 -nv -A.html https://devguide.python.org/

# Find all downloaded HTML files and extract the text
find ./devguide.python.org -type f -iname "*.html" -exec python extract_text.py {} \;

# Remove the original HTML files (optional)
find ./devguide.python.org -type f -iname "*.html" -exec rm {} \;

# python3 ingest.py
