FROM ubuntu:latest
RUN apt update && apt install -y python3 python3-pip iptables ipset
WORKDIR /app
COPY . .
RUN pip install requests
#CMD [ "python3", "badboys.py" ]