FROM python:alpine
COPY ./www /www
WORKDIR /www
RUN pip install -r requirements.txt
CMD ["gunicorn", "-w 2", "cloudgpu:app"]
