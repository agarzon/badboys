FROM python:3
RUN apt update && apt install -y python3 python3-pip ipset dnsutils
WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

#CMD [ "python", "badboys.py" ]

CMD tail -f /dev/null