FROM python:2
RUN pip install scrapy colorlog
ADD ./Archive ./
CMD [ "scrapy", "crawl", "forrester" ]
