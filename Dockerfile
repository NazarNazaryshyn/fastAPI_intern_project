FROM python

WORKDIR /src

COPY ./requirements.txt .

RUN pip install -r ./requirements.txt

COPY . .

EXPOSE 8000