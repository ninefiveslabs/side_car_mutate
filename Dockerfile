FROM python:alpine3.11
RUN pip install flask jsonpatch
COPY mutate.py mutate.py
CMD python mutate.py