from datetime import datetime

import psycopg2
import requests
import tomli

with open("conf.toml", "rb") as f:
    c = tomli.load(f)


# Generate date of when job runs
current_date = datetime.now().date()
formatted_date = current_date.strftime("%Y-%m-%d")


location = "Poole"


def get_daily_weather_data() -> dict:
    """Get current weather from Poole, Dorset of job run time"""
    response = requests.get(
        f"http://api.weatherstack.com/current?access_key={c['weatherstack']['key']}&query={location}&historical_date={formatted_date}&units=m"
    )

    try:
        if response.status_code == 200 and response is not None:
            data = response.json()
            return data["current"]
    except Exception as e:
        raise e


def insert_data_to_db():
    weather_data = get_daily_weather_data()

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
                        observation_time, temperature, wind_speed, wind_degree, wind_dir, pressure, feelslike, uv_index, visibility
                    )
                    VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s
                    );
                """,
                (
                    weather_data["observation_time"],
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
