# Basic DataEng Project #1

This is a simple project that pulls data from the WeatherStack API via the Python `requests` library. It's then pushed
into Postgres via `psycopg2` which then is displayed via a React project and Chart.js.

![dataeng project idea](images/project.png)

Libaries and Framesworks used in this project

- [WeatherStack API](https://weatherstack.com/documentation)
- [Requests library](https://requests.readthedocs.io/en/latest/)
- [Psycopg2](https://www.psycopg.org/docs/)
- [React](https://react.dev/)
- [Chart.js](https://react-chartjs-2.js.org/)
- [Docker](https://www.docker.com/)

The reason I wanted to create this project was to mess around with Postgres locally or via Docker. All Postgres projects I have completed recently have been using [Supabase](https://supabase.com/) which has been amazing but doesn't give me experience with handling Postgres via Docker or locally.

I simply wanted to create the above image.

- Pull some data from an API via `requests`
- Process data and insert into Postgres using `pysopg2`
- Create data visualisation

#### Example response

With the WeatherStack API I only wanted to store a select number of data points, I wanted to use the whole of the `current` object but also use the `localtime` and `localtime_epoc` from the `location` object. I used the `datetime` library to format the `localtime` key to a date and a time. While storing the epoc time as it is.

```json
{
  "request": {
    "type": "City",
    "query": "Poole, United Kingdom",
    "language": "en",
    "unit": "m"
  },
  "location": {
    "name": "Poole",
    "country": "United Kingdom",
    "region": "Dorset",
    "lat": "50.723",
    "lon": "-1.980",
    "timezone_id": "Europe/London",
    "localtime": "2023-08-22 19:07",
    "localtime_epoch": 1692731220,
    "utc_offset": "1.0"
  },
  "current": {
    "observation_time": "06:07 PM",
    "temperature": 21,
    "weather_code": 116,
    "weather_icons": [
      "https://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0002_sunny_intervals.png"
    ],
    "weather_descriptions": [
      "Partly cloudy"
    ],
    "wind_speed": 17,
    "wind_degree": 260,
    "wind_dir": "W",
    "pressure": 1020,
    "precip": 0,
    "humidity": 64,
    "cloudcover": 25,
    "feelslike": 21,
    "uv_index": 5,
    "visibility": 10,
    "is_day": "yes"
  }
}
```

#### Table for weather data

This is the code block for the table creation. Using `SERIAL` here to autoincrement the `id`. I wanted to keep the rest of the datapoints in their original data formats. Pretty simple as most of them are `INTs` this project was more for formatting the data and inserting into a database.

```sql
CREATE TABLE IF NOT EXISTS weather_data
(
    id          SERIAL PRIMARY KEY,
    date        DATE,
    observation_time VARCHAR(50),
    epoc_time   INT,
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

## To Run

If you want to run this pipeline you will have to sign up for a [WeatherStack](https://weatherstack.com/) account to get yourself a API key. Once you have that you can clone this repo

```bash
git clone git@github.com:mrpbennett/basic_dataeng_proj.git
```
You will need to cd into the root directory and create yourself a `conf.toml` file like the following:

```toml
[weatherstack]
key = "xxxx"

[db]
host = "xxx"
name = ' xxx'
user = 'xxx'
password = 'somepassword'
port = 5432
```

Once you have created that file. You can then install all the project dependencies, there are only 4 here.

- requests
- pytest 
- tomli 
- psycopg2

Once these have been installed you can then run the docker image for postgres with the below:

```bash
docker run --name basic-dbeng-proj-db -e POSTGRES_PASSWORD=mysecretpassword -e POSTGRES_PORT=5432 -d -p 5432:5432 postgres
```

Once there is a postgres container running you can run the script and everything fingers crossed should work! 

## Things I have learnt

- pg4admin kinda sucks, and I should learn more on how to use the CLI. 
- The `IF NOT EXISTS` command is pretty neat if you're trying to create a table on initial load but don't want to run into errors the next time your script runs.
- Not to use f strings when typing up queries, and to use placeholders `%s` as this is to prevent SQL injection. For example:

```python
curr.execute(
    """
    INSERT INTO some_table (name, job_title)
    VALUES ( %s, %s);
    """,
    ('Paul Bennett', 'Senior Solutions Eng'),
)

```

- You can unpack this `psycopg2.connect(**c["db"])` to make using multiple items easier


## ToDo:

- Build React front end for data visualisation [ ]
- Write some tests for data integrity [ ]
