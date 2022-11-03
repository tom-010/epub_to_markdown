FROM python:3.10-slim-bullseye

# For gcc:
RUN echo 'deb http://deb.debian.org/debian testing main' >> /etc/apt/sources.list
RUN apt update -y
RUN apt install -y gcc

# pandoc
RUN apt install -y pandoc

RUN mkdir /code
COPY requirements.txt /code/
WORKDIR /code

RUN pip3 install --upgrade pip
RUN pip3 install -v spacy
RUN python3 -m spacy download en_core_web_sm

RUN pip3 install -r requirements.txt

COPY . /code

ENTRYPOINT [ "python", "/code/epub_to_md.py" ]


