FROM python:3.12-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True
ENV APP_HOME /app

WORKDIR $APP_HOME

COPY . ./
COPY requirements.txt ./

# Install production dependencies.
RUN pip install --upgrade pip && pip install --check-build-dependencies --no-cache-dir --compile -U \
    -r requirements.txt && rm requirements.txt
RUN chmod +x entrypoint.sh
ENV PATH=/root/.local/bin:$PATH

# Entrypoint file witch optionally configure google auth from the credentials file
ENTRYPOINT [ "/app/entrypoint.sh" ]

# Run the application
CMD [ "backend" ]