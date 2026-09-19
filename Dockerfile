FROM python:3.9
RUN git clone -b IXALL-Userbot https://github.com/ixally/IXALL-Userbot /home/IXALLUserbot/ \
    && chmod 777 /home/IXALLUserbot \
    && mkdir /home/IXALLUserbot/bin/

COPY ./sample_config.env ./config.env* /home/IXALLUserbot/

WORKDIR /home/IXALLUserbot/

RUN pip install --upgrade pip
RUN pip install --upgrade pip setuptools wheel
RUN pip install av
RUN pip install av --no-binary av
RUN pip install -r requirements.txt

CMD ["bash","start"]
