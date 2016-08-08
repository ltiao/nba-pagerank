FROM node:6.3.1

RUN npm install -g redis-commander

EXPOSE 32512
CMD ["redis-commander", "--port=32512", "--redis-host=redis-master"]