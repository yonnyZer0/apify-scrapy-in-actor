FROM python:2
RUN pip install scrapy
ADD ./* ./

CMD ["CD","Archive"]
CMD [ "scrapy", "crawl", "forrester" ]
