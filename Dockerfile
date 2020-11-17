FROM python

ENV SRC_DIR /app

WORKDIR ${SRC_DIR}

ADD . ${SRC_DIR}

ENV PYTHONUNBUFFERED=1

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

CMD python main.py