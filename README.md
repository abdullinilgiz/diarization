# Speaker diarization - task for Abdullin Ilgiz
### How to start service in docker container
First of all you need to put base whisper model in `app/whisper_model` folder. You can find the right model [here](https://disk.yandex.ru/d/sq2YXlmIFbfSZA).

Then in root folder of the repository do the following steps.
```bash
docker build -t myapp .
```
```bash
docker run -p 8000:8000 myapp
```
Great! Service availible on the port 8000 of your local machine.

Also you can check audio files I used to check the service quality and speed  via the [link](https://disk.yandex.ru/d/y5hQ8qiZrJ-ETQ).
