FROM alpine
RUN apk add build-base python3 python3-dev libffi-dev

COPY . .
RUN python3 -m pip install -r requirements.txt
EXPOSE 5000

CMD python3 routes.py