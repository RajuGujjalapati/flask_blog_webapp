FROM centos:latest
RUN yum install net-tools-y
RUN yum install httpd-y
RUN yum install python3 -y
COPY requirements.txt /home
RUN pip3 install -r /home/requirements.txt
COPY FLASK_BLOG_WEBAPP WEB_APP
WORKDIR /WEB_APP
ENTRYPOINT [ "python3", "app.py" ]
EXPOSE 3000 5000