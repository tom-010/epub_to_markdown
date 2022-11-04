import re 
import os
import spacy
import shutil
from slugify import slugify
import subprocess
import argparse

def main():
    parser = argparse.ArgumentParser(description='Converts an EPUB file to a Markdown file')
    parser.add_argument('--epub', required=True, help='Path to the EPUB File')
    parser.add_argument('--out', required=True, help='Path where the folder for the Markdown and its images will be created')
    args = parser.parse_args()


    path_to_markdown = epub_to_markdown(args.epub, args.out)
    post_process(path_to_markdown, args.out)


def post_process_content(book_slug, content, out, copy_images=True):
    nlp = spacy.load("en_core_web_sm")
  
    # remove <div>
    content = re.sub(r'<\/?div.*>', '', content)

    # unify symbols
    content = content.replace("`", "'").replace("´", "'").replace('‘', "'").replace("’", "'").replace('“', '"').replace('”', '"').replace('•', '-')
    content = content.replace('\\$', '$').replace('\\.', '.')

    # too much whitespace at enumerations

    # remove junk
    content = re.sub(r"'''\{=html\}.*'''", '', content, flags=re.S)

    # no line breaks in paragraphs
    def r(s):
        s = s[0].split('\n')
        return f'{s[0]} {s[1]}'
    content = re.sub(r'([^\n])\n([^\n])', r, content)

    # line break lists
    content = content.replace(' - ', '\n- ')

    # remove repeated line breaks
    content = re.sub(r'\n\n\n+', '\n\n', content)

    # Remove internal links
    content = re.sub(r'\[(.*)\]\(#(.*?)\)', lambda m: m[1], content)

    # No formatting in header
    content = re.sub(r'^#+ .*', lambda match: match[0].replace('*', '').replace('__', ''), content, flags=re.MULTILINE)

    # No links in header
    content = re.sub(r'^(#+ )\[(.*)\]\(.*\)', lambda m: m[1] + m[2], content, flags=re.MULTILINE)

    # add an addional line break before every heading
    content = re.sub(r'\n#+ ', lambda s: f'\n{s[0]}', content)

    # Fix duplicate images
    def dup_img(s):
        s = str(s[0])
        left = s[0:len(s) // 2]
        if s == left + left:
            return left
        else:
            return s
    content = re.sub(r'(!\[.*\]\(.*\))(!\[.*\]\(.*\))', dup_img, content)

    # Fix capslock headings
    def fix_case(heading):    
        if not heading.isupper():
            return heading

        doc = nlp(heading)
        res = []
        for word in doc:
            w = str(word)
            first_letter = w[0].upper() if word.tag_ == 'NNP' else w[0].lower()
            res.append(first_letter + (w[1:].lower() or ''))

        res = ' '.join(res)
        res = res[0].upper() + res[1:]
        res = re.sub(r" ('|\?|!|\.|#)", lambda s: s[0].strip(), res)
        return res


    # Fix images
    def new_img_filename(name):
        res = name
        res = res.split('/')[-1]
        res = f'img_epub_{book_slug}_{res}'
        return res
    def move_and_replace_img(match):
        alt = match[1]
        old_file_name = match[2]
        old_file_name = old_file_name.split(')')[0] # an ugly hack, as this group extends to the last ')' of the line. Better solution is to reduce greedyness
        file_name = new_img_filename(old_file_name)
        if copy_images:
            try:
                if not os.path.isfile(f'{out}/{book_slug}/{file_name}'):
                    shutil.copyfile(old_file_name, f'{out}/{book_slug}/{file_name}')
            except Exception as e:
                print(e)
        return f'![{alt}]({file_name})' 
    content = re.sub(f'!\[(.*)\]\((.*)\)', move_and_replace_img, content)

    # Make headings not capslock
    content = re.sub(r'\n(#+) (.*)\n', lambda heading: '\n'+ heading[1] + ' ' + fix_case(heading[2]) + '\n', content)

    

    return content 

def path_to_name(path):
    return '.'.join(path.split('/')[-1].split('.')[:-1])

def epub_to_markdown(path_to_epub, out):
    path_to_epub = os.path.expanduser(path_to_epub)
    book_name = path_to_name(path_to_epub)
    book_slug = slugify(book_name)
    markdown_parent_folder = f'{out}/{book_slug}'
    os.makedirs(markdown_parent_folder, exist_ok=True)
    markdown_path = f'{markdown_parent_folder}/{book_name}.md'

    # convert
    command = [
        f'pandoc',
        f'--data-dir=data',
        f'--read=EPUB',
        f'--write=markdown_mmd',
        f'--markdown-headings=atx',
        f'--top-level-division=chapter',
        f'--output={markdown_path}',
        f'--extract-media=out',
        f'--lua-filter=remove-attr.lua',
        path_to_epub
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    _, error = process.communicate()
    
    if error:
        print(error)
        exit(1)
    if process.returncode != 0:
        exit(1)
    return markdown_path

def post_process(path_to_markdown, out):
    with open(path_to_markdown) as f:
        content = f.read()
    book_name = path_to_name(path_to_markdown)
    book_slug = slugify(book_name)
    content = post_process_content(book_slug, content, out)
    with open(path_to_markdown, 'w') as f:
        f.write(content)


def dev():
    # path = 'in.epub'
    # p = epub_to_markdown(path, 'out')

    with open('out/in/in.md') as f:
        content = f.read()

    content = post_process_content('in', content, 'out.md', copy_images=False)

    with open('out/in/out.md', 'w') as f:
        f.write(content)

#dev()
# main()