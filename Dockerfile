FROM python:3
RUN pip3 install scrapy
COPY ./* ./
CMD [ "scrapy", "crawl", "forrester" ]
