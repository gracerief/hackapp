FROM alpine
RUN apk add python3

COPY . .
RUN python3 -m pip install -r requirements.txt
EXPOSE 5000

CMD python3 src/routes.py