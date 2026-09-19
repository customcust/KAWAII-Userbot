FROM python:3.9
RUN git clone -b KAWAII-Userbot https://github.com/customcust/KAWAII-Userbot /home/KAWAIIUserbot/ \
    && chmod 777 /home/KAWAIIUserbot \
    && mkdir /home/KAWAIIUserbot/bin/

COPY ./sample_config.env ./config.env* /home/KAWAIIUserbot/

WORKDIR /home/KAWAIIUserbot/

RUN pip install --upgrade pip
RUN pip install --upgrade pip setuptools wheel
RUN pip install av
RUN pip install av --no-binary av
RUN pip install -r requirements.txt

CMD ["bash","start"]
