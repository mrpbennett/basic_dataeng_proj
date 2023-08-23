import psycopg2
import requests
import tomli
from datetime import datetime

import json

with open("conf.toml", "rb") as f:
    c = tomli.load(f)

location = "Poole"


def get_daily_weather_data() -> dict:
    """Get current weather from Poole, Dorset of job run time"""
    response = requests.get(
        f"http://api.weatherstack.com/current?access_key={c['weatherstack']['key']}&query={location}"
    )

    try:
        if response.status_code != 200 or response is None:
            return {"message": "no data returned"}

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


def create_weather_data_table():
    """create the relevant table needed, this is needed for inital project run"""
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


def main():
    try:
        insert_data_to_db()
    except psycopg2.Error as e:
        raise e


if __name__ == "__main__":
    main()
