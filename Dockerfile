FROM python

ENV SRC_DIR /app

WORKDIR ${SRC_DIR}

ADD . ${SRC_DIR}

ENV PYTHONUNBUFFERED=1

CMD python main.py