FROM python:2
RUN pip install scrapy colorlog nameparser
ADD ./Archive ./
CMD [ "scrapy", "crawl", "forrester" ]
