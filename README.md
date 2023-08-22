# Basic DataEng Project #1

This is a simple project that pulls data from the WeatherStack API via the Python `requests` library. It's then pushed
into Postgres via `psycopg2` which then is displayed via a React project and Chart.js.

![dataeng project idea](images/project.png)

- [WeatherStack API](https://weatherstack.com/documentation)

The reason I wanted to create this project was to mess around with Postgres locally or via Docker. All Postgres projects I have completed recently have been using [Supabase](https://supabase.com/) which has been amazing but doesn't give me experience with handling Postgres via Docker or locally.

I simply wanted to create the above image.

- Pull some data from an API via `requests`
- Process data and insert into Postgres using `pysopg2`
- Create data visualisation

##### Example response

With the WeatherStack API I am only interested in the `current` weather. I want to log the current weather of when the
job runs.

```json
{
  "observation_time": "01:44 PM",
  "temperature": 23,
  "weather_code": 116,
  "weather_icons": [
    "https://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0002_sunny_intervals.png"
  ],
  "weather_descriptions": [
    "Partly cloudy"
  ],
  "wind_speed": 15,
  "wind_degree": 240,
  "wind_dir": "WSW",
  "pressure": 1021,
  "precip": 0,
  "humidity": 61,
  "cloudcover": 25,
  "feelslike": 25,
  "uv_index": 6,
  "visibility": 10,
  "is_day": "yes"
}
```

##### Table for weather data

Here I only wanted to capture a select number of items from the returned `current` response, this is the table that was
created:

```sql
CREATE TABLE weather_data
(
    id          SERIAL PRIMARY KEY,
    observation_time VARCHAR(50),
    temperature INT,
    wind_speed  INT,
    wind_degree INT,
    wind_dir    VARCHAR(10),
    pressure    INT,
    feelslike   INT,
    uv_index    INT,
    visibility  INT
);
```

```bash
docker run --name basic-dbeng-proj-db -e POSTGRES_PASSWORD=mysecretpassword -e POSTGRES_PORT=5432 -d -p 5432:5432 postgres
```