FROM python:alpine

COPY $(pwd)/www/requirements.txt /www
WORKDIR /www
RUN pip install -r requirements.txt

COPY $(pwd)/www /www

EXPOSE 5000
CMD ["gunicorn", "-w 2", "-b 0.0.0.0:5000", "cloudgpu:app"]