FROM python:alpine
#RUN mkdir -p /www
COPY ./www/requirements.txt /www/
WORKDIR /www
RUN pip install -r requirements.txt
COPY ./www /www
#ENV LISTEN_PORT=5000
#EXPOSE 5000
#CMD ["gunicorn", "-w 2", "cloudgpu:app"]
CMD ["gunicorn", "-w 2", "-b 0.0.0.0:5000", "cloudgpu:app"]
#CMD ["python", "cloudgpu.py"]
