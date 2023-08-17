FROM python

WORKDIR /usr/src/app

COPY requirements.txt ./

COPY . .

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

EXPOSE 8081/tcp 8082/tcp

