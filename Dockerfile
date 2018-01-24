FROM python:2
RUN pip install scrapy
COPY ./* ./
CMD ["ls"]
CMD [ "scrapy", "crawl", "forrester" ]
