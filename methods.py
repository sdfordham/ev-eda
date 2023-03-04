import urllib3
from bs4 import BeautifulSoup
import pandas as pd


def get_webpage(url="https://ev-database.org/"):
    http = urllib3.PoolManager()
    res = http.request("GET", url)
    http.clear()
    return res


def process_webpage(res):
    soup = BeautifulSoup(res.data, "html.parser")
    car_list = soup.find("div", attrs={"class": "list"})
    cars_divs = car_list.find_all("div", attrs={"class": "list-item"})

    cars = list()
    for div in cars_divs:
        car = list()
        for span in div.find_all("span"):
            if "class" in span.attrs and span.contents:
                car.append(
                    {
                        "class": span.attrs["class"],
                        "contents": span.contents[0]
                    }
                )
        cars.append(car)

    cars_processed = list()
    for car in cars:
        this_ = dict()

        # Get maker/manufacturer (first span)
        this_["maker"] = car[0]["contents"]

        # Get bunch of details
        for detail in ("model", "battery", "acceleration",
            "topspeed", "erange_real", "efficiency", "fastcharge_speed",
            "country_de", "country_nl", "country_uk"
            ):
            for aspect in car:
                if detail in aspect["class"]:
                    this_[detail] = aspect["contents"]
                    break
            if detail not in this_:
                this_[detail] = None

        
        # Get plug type
        for aspect in car:
            for class_ in aspect["class"]:
                if class_.lower().startswith("plug"):
                    this_["plug"] = aspect["contents"]
                    break
            this_[detail] = None

        cars_processed.append(this_)
    return cars_processed


def make_dataframe(cars):
    df = pd.DataFrame.from_dict(cars)
    df = df.astype(
        {
            "maker": "string",
            "model": "string",
            "battery": "float64",
            "fastcharge_speed": "float64",
            "plug": "string"
        }
    )
    df["acceleration (sec)"] = df["acceleration"].str.extract("(\d+.\d+)\ssec").astype("float64")
    df["topspeed (km/h)"] = df["topspeed"].str.extract("(\d+)\skm\/h").astype("int64")
    df["erange_real (km)"] = df["erange_real"].str.extract("(\d+)\skm").astype("int64")
    df["efficiency (Wh/km)"] = df["efficiency"].str.extract("(\d+)\sWh\/km").astype("int64")

    for price in ("country_de", "country_nl", "country_uk"):
        if df[price].isna().all():
            continue
        match = df[price].str.extract("€(\d+),(\d+)")
        df[f"{price} (€)"] = (
            match[~match.isna().any(axis=1)]
            .agg("".join, axis=1)
            .astype("float64")
        )

    df.drop(
        columns=
        [
            "acceleration", "topspeed", "erange_real", "efficiency",
            "country_de", "country_nl", "country_uk"
        ],
        inplace=True
    )

    return df
