EPUB to Markdown
================

Convets an EPUB-Ebook to Markdown such that it can be used then in Markdown-Editors.

## Install

Make sure, docker is running.

Put the `scripts/run.sh`, make it executable and put it int `/usr/bin/epub_to_markdown`.
You don't have to clone the repo. 
But if you did, you can use `./scripts/install.sh` to do just that.

After that, go to the directory, where your Epub is and run: `epub_to_markdown file.epub`.
This will create a `out` folder (or reuses it) where you can find the output consisting of the markdown and its images.

## Why is the image so big?

It includes pandoc and a dictionary, to make CAPS LOCK HEADLINES normal.