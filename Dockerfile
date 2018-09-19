FROM python:alpine
RUN mkdir -p /www
COPY ./www /www
WORKDIR /www/
RUN pip install -r requirements.txt
CMD ["gunicorn", "-w 2", "-b 0.0.0.0:5000", "cloudgpu:app"]
