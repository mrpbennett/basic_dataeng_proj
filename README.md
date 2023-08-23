# My super simple data pipeline

As I have started to explore the Data Engineer role and learn more about the processes, required skills and other items related to the role. I have created a super simple data pipeline.

This is a simple project that pulls data from the WeatherStack API via the Python `requests` library. It's then pushed into Postgres via `psycopg2` which then is displayed via a React project and Chart.js.

![dataeng project idea](images/project.png)

Libraries and Frameworks used in this project

- [WeatherStack API](https://weatherstack.com/documentation)
- [Requests library](https://requests.readthedocs.io/en/latest/)
- [Psycopg2](https://www.psycopg.org/docs/)
- [React](https://react.dev/)
- [Chart.js](https://react-chartjs-2.js.org/)
- [Docker](https://www.docker.com/)

The reason I wanted to create this project was to mess around with Postgres locally or via Docker. All Postgres projects I have completed recently have been using [Supabase](https://supabase.com/) which has been amazing but doesn't give me experience with handling Postgres via Docker or locally.

I simply wanted to create the above image.

- Pull some data from an API via `requests`
- Process data and insert it into Postgres using `pysopg2`
- Create data visualisation

#### Example response

With the WeatherStack API, I only wanted to store a select number of data points, I wanted to use the whole of the `current` object but also use the `localtime` and `localtime_epoc` from the `location` object. I used the `datetime` library to format the `localtime` key to a date and a time. While storing the epoch time as it is.

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

#### Pulling the weather data

As mentioned above I only wanted to use select items from the response. I didn't want to use the original from `observation_time`. I decided to use `datetime.strptime` to format mate the value from `localtime` as this had the data and time of the response.

```python
"date": datetime.strptime(data["location"]["localtime"], "%Y-%m-%d %H:%M").date(),
"observation_time": datetime.strptime(data["location"]["localtime"], "%Y-%m-%d %H:%M").time(),
```

The full function `get_daily_weather_data` looks like the one below. The rest of the data is untouched by the `current` object.


```python
def get_daily_weather_data() -> dict:
    """Get current weather from Poole, Dorset of job run time"""
    response = requests.get(
        f"http://api.weatherstack.com/current?access_key={c['weatherstack']['key']}&query={location}"
    )

    try:
        if response.status_code == 200 and response is not None:
            data = response.json()

            return {
                "date": datetime.strptime(
                    data["location"]["localtime"], "%Y-%m-%d %H:%M"
                ).date(),
                "observation_time": datetime.strptime(
                    data["location"]["localtime"], "%Y-%m-%d %H:%M"
                ).time(),
                "epoc_time": data["location"]["localtime_epoch"],
                "temperature": data["current"]["temperature"],
                "wind_speed": data["current"]["wind_speed"],
                "wind_degree": data["current"]["wind_degree"],
                "wind_dir": data["current"]["wind_dir"],
                "pressure": data["current"]["pressure"],
                "feelslike": data["current"]["feelslike"],
                "uv_index": data["current"]["uv_index"],
                "visibility": data["current"]["visibility"],
            }

    except Exception as e:
        raise e
```

#### Table for weather data

This is the code block for the table creation. Using `SERIAL` here to autoincrement the `id`. I wanted to keep the rest of the data points in their original data formats. Pretty simple as most of them are `INTs` this project was more for formatting the data and inserting it into a database.

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

This is how I created the table, this function does run every time the script runs, but with `CREATE TABLE IF NOT EXISTS` the query won't throw any errors if the table already exists.

```python
def create_weather_data_table():
    """create the relevant table needed, this is needed for initial project run"""
    with psycopg2.connect(
        dbname=c["db"]["name"],
        user=c["db"]["user"],
        password=c["db"]["password"],
        host=c["db"]["host"],
        port=c["db"]["port"],
    ) as conn:
        with conn.cursor() as curs:
            curs.execute(
                """
                    CREATE TABLE IF NOT EXISTS weather_data
                        (
                            id          SERIAL PRIMARY KEY,
                            date DATE,
                            observation_time VARCHAR(50),
                            epoc_time INT,
                            temperature INT,
                            wind_speed  INT,
                            wind_degree INT,
                            wind_dir    VARCHAR(10),
                            pressure    INT,
                            feelslike   INT,
                            uv_index    INT,
                            visibility  INT
                        );
                """
            )
```

I then have another simple function that calls the `get_daily_weather_data` function storing the data inside a variable, before calling the `create_weather_data_table` function to create the table if it doesn't exist, it then inserts the `weather_data` data into that table. 

Here we're using Postgres placeholders `%s` over f strings this is to prevent things like SQL injection.


```python
def insert_data_to_db():
    weather_data = get_daily_weather_data()

    # create weather_data if it doesn't exist before uploading data
    create_weather_data_table()

    with psycopg2.connect(
        dbname=c["db"]["name"],
        user=c["db"]["user"],
        password=c["db"]["password"],
        host=c["db"]["host"],
        port=c["db"]["port"],
    ) as conn:
        with conn.cursor() as curs:
            curs.execute(
                """
                    INSERT INTO weather_data (
                        date, observation_time, epoc_time, temperature, wind_speed, wind_degree, wind_dir, pressure, feelslike, uv_index, visibility
                    )
                    VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    );
                """,
                (
                    weather_data["date"],
                    weather_data["observation_time"],
                    weather_data["epoc_time"],
                    weather_data["temperature"],
                    weather_data["wind_speed"],
                    weather_data["wind_degree"],
                    weather_data["wind_dir"],
                    weather_data["pressure"],
                    weather_data["feelslike"],
                    weather_data["uv_index"],
                    weather_data["visibility"],
                ),
            )

    conn.close()
```

## To Run

If you want to run this pipeline you will have to sign up for a [WeatherStack](https://weatherstack.com/) account to get yourself a API key. Once you have that you can clone this repo

```bash
git clone git@github.com:mrpbennett/basic_dataeng_proj.git
```
You will need to cd into the root directory and create a `conf.toml` file like the following:

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

Once these have been installed you can then run the docker image for Postgres with the below:

```bash
docker run --name basic-dbeng-proj-db -e POSTGRES_PASSWORD=mysecretpassword -e POSTGRES_PORT=5432 -d -p 5432:5432 postgres
```

Once there is a Postgres container running you can run the script and everything fingers crossed should work! 

## Things I have learnt

- pg4admin kinda sucks, and I should learn more about how to use the CLI. 
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



