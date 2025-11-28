import requests
import customtkinter as custom
from tkinter import StringVar
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime as dt

global_font = ("Courier", 13)
global_font_bold = ("Courier", 14, "bold")
title_font = ("Courier", 22, "bold")

headers = {
    "x-rapidapi-key": "e889f233f5mshf03e68f0a2e754dp185c15jsnde87d57f25df",
    "x-rapidapi-host": "sunrise-sunset-times.p.rapidapi.com"
}

custom.set_appearance_mode("light")
custom.set_default_color_theme("blue")

def GetCoordinates(city: str):
    coor_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en"
    resp = requests.get(coor_url).json()
    if "results" not in resp or len(resp["results"]) == 0:
        raise ValueError("City not found")
    result = resp["results"][0]
    lat = result["latitude"]
    lon = result["longitude"]
    name = result.get("name", city)
    country = result.get("country", "")
    location_name = f"{name}, {country}" if country else name
    return float(lat), float(lon), location_name

def GetSunTimes(lat: float, lon: float, date: str, tz_id: str):
    url = "https://sunrise-sunset-times.p.rapidapi.com/getSunTimes"
    params = {"latitude": lat, "longitude": lon, "date": date, "timeZoneId": tz_id}
    r = requests.get(url, headers=headers, params=params, timeout=10)
    r.raise_for_status()
    j = r.json()
    return {"sunrise": j.get("sunrise"), "sunset": j.get("sunset")}

def Get5DayForecast(lat: float, lon: float):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,relativehumidity_2m&forecast_days=5"
    r = requests.get(url)
    r.raise_for_status()
    j = r.json()
    times = [dt.fromisoformat(t).strftime("%m-%d %H:%M") for t in j["hourly"]["time"]]
    temps = j["hourly"]["temperature_2m"]
    hums = j["hourly"]["relativehumidity_2m"]
    return times, temps, hums

class MainGUI(custom.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sunrise, Sunset & 5-Day Forecast")
        self.geometry("1100x700")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        main = custom.CTkFrame(self, fg_color="#f8cadd", corner_radius=0)
        main.grid(row=0, column=0, sticky="nswe", padx=12, pady=12)
        main.grid_columnconfigure(0, weight=1)

        custom.CTkLabel(main, text="Sunrise, Sunset & 5-Day Forecast", font=title_font, text_color="black").grid(row=0, column=0, pady=(10,6))

        input_frame = custom.CTkFrame(main, fg_color="#f8cadd")
        input_frame.grid(row=1, column=0, sticky="we", pady=6)
        for i in range(3):
            input_frame.grid_columnconfigure(i, weight=1)

        self.location_entry = custom.CTkEntry(input_frame, placeholder_text="Input location here", font=global_font)
        self.location_entry.grid(row=0, column=0, padx=8, pady=6, sticky="we")

        self.timezone_box = custom.CTkComboBox(input_frame, values=["UTC+8", "UTC+0", "EST (UTC-5)", "CET (UTC+1)"], width=150, font=global_font, dropdown_font=global_font)
        self.timezone_box.set("UTC+8")
        self.timezone_box.grid(row=0, column=1, padx=8, pady=6)

        self.date_var = StringVar()
        self.date_var.set(str(datetime.date.today()))
        self.date_entry = custom.CTkEntry(input_frame, textvariable=self.date_var, placeholder_text="DATE (YYYY-MM-DD)", font=global_font)
        self.date_entry.grid(row=0, column=2, padx=8, pady=6, sticky="we")

        self.submit_btn = custom.CTkButton(input_frame, text="Submit", command=self.submit, font=global_font_bold)
        self.submit_btn.grid(row=0, column=3, padx=8, pady=6)

        self.sun_panel = custom.CTkFrame(main, fg_color="#ffffff", corner_radius=18, height=160)
        self.sun_panel.grid(row=2, column=0, sticky="we", padx=16, pady=(10,6))
        self.sun_panel.grid_propagate(False)
        self.sun_title_var = StringVar()
        self.sun_text_var = StringVar()
        custom.CTkLabel(self.sun_panel, textvariable=self.sun_title_var, font=global_font_bold, text_color="black").pack(pady=(10,0))
        custom.CTkLabel(self.sun_panel, textvariable=self.sun_text_var, wraplength=700, justify="center", text_color="black", font=global_font).pack(pady=(6,10))

        self.forecast_panel = custom.CTkFrame(main, fg_color="#ffffff", corner_radius=18, height=450)
        self.forecast_panel.grid(row=3, column=0, sticky="we", padx=16, pady=(6,10))
        self.forecast_panel.grid_propagate(False)
        self.forecast_title_var = StringVar()
        self.forecast_title_var.set("5-Day Forecast (3-Hour Intervals)")
        custom.CTkLabel(self.forecast_panel, textvariable=self.forecast_title_var, font=global_font_bold, text_color="black").pack(pady=(10,0))

        self.set_idle_texts()

    def set_idle_texts(self):
        self.sun_title_var.set("Sunrise & Sunset")
        self.sun_text_var.set("Enter a location and click Submit.")

    def submit(self):
        self.submit_btn.configure(state="disabled", text="Working...")
        try:
            city = self.location_entry.get().strip()
            date = self.date_var.get().strip()
            tz_map = {"UTC+8": "UTC+8", "UTC+0": "UTC+0", "EST (UTC-5)": "UTC-5", "CET (UTC+1)": "UTC+1"}
            tz = tz_map[self.timezone_box.get()]
            self.lat, self.lon, location_name = GetCoordinates(city)
            sun = GetSunTimes(self.lat, self.lon, date, tz)
            sun_title = f"Sun times for {location_name} on {date}"
            lines = []
            if sun.get("sunrise"): lines.append(f"Sunrise: {sun['sunrise']}")
            if sun.get("sunset"): lines.append(f"Sunset:  {sun['sunset']}")
            self.sun_title_var.set(sun_title)
            self.sun_text_var.set("\n".join(lines))

            times, temps, hums = Get5DayForecast(self.lat, self.lon)

            for widget in self.forecast_panel.winfo_children():
                widget.destroy()
            custom.CTkLabel(self.forecast_panel, textvariable=self.forecast_title_var, font=global_font_bold, text_color="black").pack(pady=(10,0))

            fig, ax = plt.subplots(figsize=(14, 5))
            fig.patch.set_facecolor("white")
            ax.set_facecolor("white")

            marker_interval = max(1, len(times) // 20)

            ax.plot(times, temps, color="#1f77b4", marker="o", markevery=marker_interval, markersize=6, linewidth=2, label="Temperature (°C)")
            ax.plot(times, hums, color="#ff7f0e", marker="s", markevery=marker_interval, markersize=6, linewidth=2, label="Humidity (%)")

            ax.set_ylabel("Value")
            ax.set_ylim(min(min(temps), min(hums)) - 5, max(max(temps), max(hums)) + 5)

            ax.grid(True, which="both", linestyle="--", linewidth=0.6, alpha=0.6)

            xtick_step = max(1, len(times) // 20)
            ax.set_xticks(range(0, len(times), xtick_step))
            ax.set_xticklabels([times[i] for i in range(0, len(times), xtick_step)], rotation=45, ha="right")

            ax.set_title("3-Hour Temperature & Humidity Forecast (Next 5 Days)", fontsize=16, pad=14)
            ax.legend(loc="upper left")

            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=self.forecast_panel)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

        except Exception as e:
            self.sun_text_var.set("Error: " + str(e))
        finally:
            self.submit_btn.configure(state="normal", text="Submit")


if __name__ == "__main__":
    app = MainGUI()
    app.mainloop()
