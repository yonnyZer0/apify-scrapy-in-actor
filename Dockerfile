FROM python:2
RUN pip install scrapy colorlog nameparser unidecode requests
ADD ./Archive ./
CMD [ "scrapy", "crawl", "gartner" ]
