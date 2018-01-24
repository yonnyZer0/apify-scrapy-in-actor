FROM python:2
RUN pip install scrapy colorlog nameparser unidecode
ADD ./Archive ./
CMD [ "scrapy", "crawl", "forrester" ]
