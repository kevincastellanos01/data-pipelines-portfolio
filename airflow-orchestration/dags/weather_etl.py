from airflow.decorators import dag, task
from datetime import datetime
import os
import json
import requests
import pandas as pd


API_URL = "https://api.open-meteo.com/v1/forecast"

# Puedes cambiar estas coordenadas si quieres otra ciudad
LOCATION_NAME = "Berlin"
LATITUDE = 52.52
LONGITUDE = 13.41


@dag(
    dag_id="weather_etl",
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["weather", "etl"]
)
def weather_etl_pipeline():

    @task
    def extract_weather() -> dict:
        """Fetch weather data from Open-Meteo API"""
        print("[EXTRACT] Starting weather extraction...")

        params = {
            "latitude": LATITUDE,
            "longitude": LONGITUDE,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
            "hourly": "temperature_2m,apparent_temperature,relative_humidity_2m",
            "timezone": "auto",
            "forecast_days": 1
        }

        try:
            response = requests.get(API_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            if "current" not in data or "hourly" not in data:
                raise ValueError("API response is missing 'current' or 'hourly' data.")

            print(f"[EXTRACT] Weather data fetched successfully for {LOCATION_NAME}")
            print(f"[EXTRACT] API URL used: {response.url}")
            return data

        except requests.RequestException as e:
            print(f"[EXTRACT][ERROR] Request failed: {e}")
            raise
        except Exception as e:
            print(f"[EXTRACT][ERROR] Unexpected error: {e}")
            raise

    @task
    def transform_weather(raw_data: dict) -> dict:
        """Transform weather data with derived fields and statistics"""
        print("[TRANSFORM] Starting weather transformation...")

        try:
            current = raw_data["current"]
            hourly = raw_data["hourly"]

            hourly_df = pd.DataFrame({
                "time": hourly["time"],
                "temperature_c": hourly["temperature_2m"],
                "feels_like_c": hourly["apparent_temperature"],
                "humidity": hourly["relative_humidity_2m"]
            })

            hourly_df["time"] = pd.to_datetime(hourly_df["time"])

            current_temp_c = float(current["temperature_2m"])
            current_feels_like_c = float(current["apparent_temperature"])
            current_humidity = float(current["relative_humidity_2m"])
            current_wind_kmh = float(current["wind_speed_10m"])
            current_weather_code = int(current["weather_code"])

            current_temp_f = round((current_temp_c * 9 / 5) + 32, 2)
            current_feels_like_f = round((current_feels_like_c * 9 / 5) + 32, 2)

            def temperature_category(temp_c: float) -> str:
                if temp_c < 10:
                    return "cold"
                elif temp_c < 20:
                    return "cool"
                elif temp_c < 28:
                    return "warm"
                else:
                    return "hot"

            def wind_category(wind_kmh: float) -> str:
                if wind_kmh < 10:
                    return "calm"
                elif wind_kmh < 25:
                    return "breezy"
                elif wind_kmh < 40:
                    return "windy"
                else:
                    return "very_windy"

            avg_temp_c = round(float(hourly_df["temperature_c"].mean()), 2)
            min_temp_c = round(float(hourly_df["temperature_c"].min()), 2)
            max_temp_c = round(float(hourly_df["temperature_c"].max()), 2)

            avg_feels_like_c = round(float(hourly_df["feels_like_c"].mean()), 2)
            avg_humidity = round(float(hourly_df["humidity"].mean()), 2)

            hottest_row = hourly_df.loc[hourly_df["temperature_c"].idxmax()]

            transformed_record = {
                "location": LOCATION_NAME,
                "latitude": raw_data["latitude"],
                "longitude": raw_data["longitude"],
                "timezone": raw_data.get("timezone", "auto"),
                "observation_time": current["time"],
                "temperature_c": round(current_temp_c, 2),
                "temperature_f": current_temp_f,
                "feels_like_c": round(current_feels_like_c, 2),
                "feels_like_f": current_feels_like_f,
                "humidity_percent": round(current_humidity, 2),
                "wind_speed_kmh": round(current_wind_kmh, 2),
                "weather_code": current_weather_code,
                "temperature_category": temperature_category(current_temp_c),
                "wind_category": wind_category(current_wind_kmh),
                "daily_avg_temp_c": avg_temp_c,
                "daily_min_temp_c": min_temp_c,
                "daily_max_temp_c": max_temp_c,
                "daily_avg_feels_like_c": avg_feels_like_c,
                "daily_avg_humidity_percent": avg_humidity,
                "hottest_hour": hottest_row["time"].strftime("%Y-%m-%d %H:%M:%S"),
                "hottest_hour_temp_c": round(float(hottest_row["temperature_c"]), 2)
            }

            summary_stats = {
                "hourly_points": int(len(hourly_df)),
                "avg_temp_c": avg_temp_c,
                "min_temp_c": min_temp_c,
                "max_temp_c": max_temp_c,
                "avg_feels_like_c": avg_feels_like_c,
                "avg_humidity_percent": avg_humidity
            }

            print(f"[TRANSFORM] Current temperature: {current_temp_c} C / {current_temp_f} F")
            print(f"[TRANSFORM] Category: {transformed_record['temperature_category']}")
            print(f"[TRANSFORM] Daily stats: {summary_stats}")

            return {
                "record": transformed_record,
                "stats": summary_stats
            }

        except Exception as e:
            print(f"[TRANSFORM][ERROR] Failed to transform data: {e}")
            raise

    @task
    def load_weather(data: dict) -> dict:
        """Save transformed weather data to CSV and JSON"""
        print("[LOAD] Saving weather files...")

        try:
            os.makedirs("/opt/airflow/data", exist_ok=True)

            run_date = datetime.now().strftime("%Y%m%d")
            csv_path = f"/opt/airflow/data/weather_{run_date}.csv"
            json_path = f"/opt/airflow/data/weather_{run_date}.json"

            df = pd.DataFrame([data["record"]])
            df.to_csv(csv_path, index=False)

            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            print(f"[LOAD] CSV saved to: {csv_path}")
            print(f"[LOAD] JSON saved to: {json_path}")

            return {
                "csv_path": csv_path,
                "json_path": json_path
            }

        except Exception as e:
            print(f"[LOAD][ERROR] Failed to save files: {e}")
            raise

    raw_data = extract_weather()
    transformed_data = transform_weather(raw_data)
    load_weather(transformed_data)


dag_instance = weather_etl_pipeline()