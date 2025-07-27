FROM python:3.13-slim

COPY init.sh /init.sh
RUN /init.sh && rm /init.sh

EXPOSE 22
ENTRYPOINT ["/usr/sbin/sshd", "-D"]