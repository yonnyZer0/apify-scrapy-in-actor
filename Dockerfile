FROM python:2
RUN pip install scrapy
COPY ./* ./
CMD [ "scrapy", "crawl", "forrester" ]
