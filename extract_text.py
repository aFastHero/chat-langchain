import sys
import os
from bs4 import BeautifulSoup

def extract_text(html_file):
    with open(html_file, 'r', encoding='utf-8') as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, 'lxml')
    text = soup.get_text()

    return text

def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_text.py [input_html_file]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = os.path.splitext(input_file)[0] + '.txt'

    text = extract_text(input_file)

    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(text)

if __name__ == '__main__':
    main()
