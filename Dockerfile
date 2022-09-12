FROM centos:latest
RUN apt-get install net-tools
RUN apt-get install httpd
RUN apt-get install python3
COPY requirements.txt /home
RUN pip3 install -r /home/requirements.txt
COPY FLASK_BLOG_WEBAPP WEB_APP
WORKDIR /WEB_APP
ENTRYPOINT [ "python3", "app.py" ]
EXPOSE 3000 5000