import pandas as pd
import plotly.express as px

"""
Cody Whitt
pkz325
CPSC 4530 Spring 2023
Assignment 1

For Dataset 2
"""

# Some helper stuff for parse_data
DOW = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
DOW_LU = {i: v for i, v in enumerate(DOW)}
ORDER_LU = {v: i for i, v in enumerate(DOW)}
EARLY_MORNING = list(range(0, 6))
LATE_MORNING = list(range(6, 12))
AFTERNOON = list(range(12, 18))
EVENING = list(range(18, 24))
TOD = ["early_morning", "late_morning", "afternoon", "evening"]
TOD_LU = {}
for i in EARLY_MORNING:
    TOD_LU[i] = TOD[0]
for i in LATE_MORNING:
    TOD_LU[i] = TOD[1]
for i in AFTERNOON:
    TOD_LU[i] = TOD[2]
for i in EVENING:
    TOD_LU[i] = TOD[3]


def parse_data():

    # Load in Raw Data
    raw_df = pd.read_csv("raw_data/Police_Incident_Data.csv")

    # Quick Look at Things
    print(raw_df.head())
    print(raw_df.info())

    # So I want date and type of crime in order to relate type of crime to time of day
    # Check potential columns of interest
    print(raw_df["Incident_Description"].unique())
    print(raw_df["Date_Incident"][:50])

    # So Looks like above two work, time of day is being stored. Lets reduce things down.
    filter_df = raw_df[["Date_Incident", "Incident_Description"]].copy()
    print(filter_df.info())

    # Some Null Incident Descriptions, but only like 500/500k, will drop
    filter_df = filter_df.dropna()
    print("Post Drop")
    print(filter_df.info())

    # Lets get a count of our incident_descriptions
    id_count = filter_df.groupby("Incident_Description")["Incident_Description"].count()
    id_count = id_count.sort_values(ascending=False)
    print(f"Incident Description Counts - Sorted:{len(id_count)}")
    for v in id_count.items():
        print(v)

    # Preferring crimes w/ the most occurrences and perhaps most associated w/ the word
    # "crime", pick out those we will look at
    keep_incidents = ["Simple Assault",
                      "Destructive/Damage/Vandalism Of Property",
                      "Shoplifting",
                      "Theft From Motor Vehicle",
                      "Drug/Narcotic Violations",
                      "Burglary/Breaking And Entering",
                      "Aggravated Assault",
                      "Motor Vehicle Theft",
                      "Driving Under The Influence",
                      "Robbery"]

    # Perform the filter to keep_incidents
    filter_df = filter_df[filter_df["Incident_Description"].isin(keep_incidents)]
    print(filter_df.head())
    print(filter_df.info())

    # Convert Date String To Date Obj
    print("Date Str -> Obj Conversion Takes a Sec..")
    filter_df["Date_Incident"] = pd.to_datetime(filter_df["Date_Incident"])
    print(filter_df.head())

    # Rename some columns
    print("Column Rename")
    filter_df = filter_df.rename(columns={"Incident_Description": "crime_type",
                                          "Date_Incident": "date_obj"})
    print(filter_df.head())

    # Add Day of Week and Hour
    filter_df["day_of_week"] = filter_df["date_obj"].apply(lambda x: DOW_LU[x.dayofweek])
    filter_df["hour_of_day"] = filter_df["date_obj"].apply(lambda x: x.hour)
    print(filter_df.head())
    print(filter_df.tail())

    # Check Num Occurrences at 00:01:00
    filter_df["potential_ignore"] = filter_df["date_obj"].apply(lambda x: [x.hour, x.minute, x.second] == [0,1,0])
    print(filter_df.head())
    print(filter_df.tail())
    print(filter_df.groupby("potential_ignore")["potential_ignore"].count())

    # So not too many, but perhaps questionable. Going to drop crimes there.
    filter_df = filter_df[~filter_df["potential_ignore"]]
    print(filter_df.head())

    # Bucket hour to get a "time of day" classification
    filter_df["time_of_day"] = filter_df["hour_of_day"].apply(lambda x: TOD_LU[x])
    print(filter_df.head())

    # Clean up a little
    filter_df = filter_df[["crime_type", "day_of_week", "time_of_day"]]
    print(filter_df.head())

    # Calc Crime Frequency
    final_df = [["crime_type", "day_of_week", "time_of_day", "crime_frequency"]]

    for crime_type in list(filter_df["crime_type"].unique()):

        print(crime_type)

        crime_df = filter_df[filter_df["crime_type"] == crime_type]  # Total Occurrences of Crimes of A Type

        for day in DOW:
            for tod in TOD:
                # Day/Time of Day to calc relative frequency
                d_t_crime_df = crime_df[(crime_df["day_of_week"] == day) &
                                        (crime_df["time_of_day"] == tod)]
                crime_freq = len(d_t_crime_df) / len(crime_df)
                final_df.append([crime_type, day, tod, crime_freq])

    final_df = pd.DataFrame(data=final_df[1:], columns=final_df[0])
    print(final_df.head())
    print(final_df.tail())
    final_df.to_csv("parsed_data/chat_crime_parsed.csv", index=False)


def plot_data():

    df = pd.read_csv("parsed_data/chat_crime_parsed.csv")

    fig = px.bar(data_frame=df, x="day_of_week", y="crime_frequency",
                 color="time_of_day", facet_col="crime_type", facet_col_wrap=2,
                 title="Chattanooga Crime Relative Crime Frequency by Day of Week and Time of Day")

    fig.show()


def main():

    parse_data()

    plot_data()


if __name__ == "__main__":

    main()
