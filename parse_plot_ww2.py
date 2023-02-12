import pandas as pd
import plotly.express as px

from plotly.subplots import make_subplots


"""
Cody Whitt
pkz325
CPSC 4530 Spring 2023
Assignment 1

For DataSet 3
"""


def parse_data():

    print("WW2 DataSet - Parse Data")

    # Read in raw .csv file
    raw_df = pd.read_csv("raw_data/operations.csv")

    # Quick Look at DataSet
    print("Raw DF Head")
    print(raw_df.head())    # Use .head() to check first 5 rows (items)
    print("Raw DF Info")
    print(raw_df.info())    # Use .info() to check columns (attributes), native data type & null counts (missing data)

    # Keep only certain attributes we are interested in (reasoning discussed in report)
    filter_df = raw_df[["Mission ID", "Mission Date", "Theater of Operations", "Aircraft Series"]]

    # Look at Attribute Filtered DataSet
    print("Filter DF Head")
    print(filter_df.head())
    print("Filter DF Info")
    print(filter_df.info())

    # Drop Null records. They represent ~2% of our items (175k remaining from 178k)
    filter_df = filter_df.dropna()
    print("Filter DF Info - Null Dropped")
    print(filter_df.info())

    # Check Unique on Mission ID
    print(len(filter_df["Mission ID"].unique()))
    print(len(filter_df))

    # Check Uniqueness and Count for our two categorical attributes
    u_theater_count = filter_df.groupby("Theater of Operations")["Theater of Operations"].count()
    u_aircraft_count = filter_df.groupby("Aircraft Series")["Aircraft Series"].count()

    print("Unique Theater Counts/Percents")
    for v in u_theater_count.items():
        print(v, round(v[1] / len(filter_df), 2) * 100.0)

    print("Unique Aircraft Counts/Percents & Quick Check to see how many over 1%")
    over_1 = 0
    for v in u_aircraft_count.items():
        print(v, round(v[1] / len(filter_df), 2) * 100.0)
        p = round(v[1] / len(filter_df), 2) * 100.0
        if p >= 1.0:
            over_1 += 1
    print(len(u_aircraft_count))
    print(over_1)

    # Drop EAST AFRICA and MADAGASCAR (reasoning discussed in report)
    filter_df = filter_df[~(filter_df["Theater of Operations"].isin(["EAST AFRICA", "MADAGASCAR"]))]
    print(filter_df["Theater of Operations"].unique())

    # Put Date on Yearly Scale (kinda hacky way, but works for this)
    filter_df["Mission Date"] = filter_df["Mission Date"].apply(lambda x: int(x.split("/")[-1]))
    print(filter_df["Mission Date"].unique())

    # Rename Columns (maybe could have done this earlier, but getting close)
    filter_df = filter_df.rename(columns={"Mission ID": "mission_id",
                                          "Mission Date": "year",
                                          "Theater of Operations": "theater",
                                          "Aircraft Series": "aircraft"})
    print(filter_df.columns)

    # Data Transformations
    # So I'm interested in how the use of a particular aircraft in a particular theater changed throughout the years,
    # both in terms to itself and to others.

    # Year (Time Data)
    # Theater (Categorical)
    # Type of Aircraft (Categorical)
    # Abs Number of Missions in unique (Year/Theater/Aircraft)
    # % of overall missions flown by an aircraft in a Theater/Year vs. total number of missions in that Theater/Year
    # % of missions flown by an aircraft in Theater/Year in relation to sum that aircraft flew in all Theater/Years

    # Calculations to be stored here
    final_df = [["year",
                 "theater",
                 "aircraft",
                 "abs_mission_count",
                 "relative_mission_count_theater_year",    # Use vs. other aircraft that year in that theater
                 "relative_mission_count_aircraft_year"]]  # Use of same aircraft compared to different years

    # This could be done more efficiently, but this steps through it clearly & allows handling of missing tuples
    for theater in list(filter_df["theater"].unique()):

        theater_df = filter_df[filter_df["theater"] == theater]  # Subset by theater
        total_missions_per_year_lu = dict(theater_df.groupby("year")["mission_id"].count())  # LU of Mission Count/year

        for aircraft in list(theater_df["aircraft"].unique()):    # Further filter by aircraft

            # All missions flown by an aircraft in a theater
            theater_aircraft_df = theater_df[theater_df["aircraft"] == aircraft]

            for year in list(theater_aircraft_df["year"].unique()):

                # All missions flown by an aircraft in a theater in a year it was present
                theater_aircraft_year_df = theater_aircraft_df[theater_aircraft_df["year"] == year]

                # Calc our desired transformations
                abs_mission_count = len(theater_aircraft_year_df)
                relative_mission_count_theater_year = abs_mission_count / total_missions_per_year_lu[year]
                relative_mission_count_aircraft_year = abs_mission_count / len(theater_aircraft_df)

                # Append
                final_df.append([year, theater, aircraft, abs_mission_count,
                                 relative_mission_count_theater_year, relative_mission_count_aircraft_year])

    final_df = pd.DataFrame(data=final_df[1:], columns=final_df[0])
    final_df = final_df.sort_values(by=['aircraft'])
    write_fp = "parsed_data/ww2_aircraft_missions_parsed.csv"
    final_df.to_csv(write_fp, index=False)

    print(f"Wrote:{write_fp}")


def plot_data():

    df = pd.read_csv("parsed_data/ww2_aircraft_missions_parsed.csv")

    # To Fix Relative Mission Count Theater Year Scale
    df["relative_mission_count_theater_year"] = df["relative_mission_count_theater_year"].apply(lambda x: max(x, 0.02))

    theaters = list(df["theater"].unique())
    theater_titles = [f"Theater:{v}" for v in theaters]
    fig = make_subplots(rows=2, cols=2, subplot_titles=theater_titles, specs=[[{"type": "polar"}, {"type": "polar"}],
                                                                              [{"type": "polar"}, {"type": "polar"}]],
                        shared_yaxes=True, shared_xaxes=True)

    r = 1
    c = 1
    for theater in theaters:
        t_df = df[df["theater"] == theater]
        sub_fig = px.scatter_polar(data_frame=t_df, r="year", theta="aircraft", range_r=[1938, 1946],
                                   size="relative_mission_count_theater_year",
                                   color="relative_mission_count_aircraft_year",
                                   color_continuous_scale="bluered")
        for v in sub_fig.select_traces():
            fig.add_trace(v, row=r, col=c)

        if r == 1 and c == 2:
            r = 2
            c = 1
        else:
            c += 1

    # Some manual adjustments
    fig.layout.polar["radialaxis"] = {'range': [1938, 1946],
                                      'tickfont': {"size": 8}}
    fig.layout.polar["angularaxis"] = {'tickfont': {"size": 8}}
    fig.layout.polar2["radialaxis"] = {'range': [1938, 1946],
                                       'tickfont': {"size": 8}}
    fig.layout.polar2["angularaxis"] = {'tickfont': {"size": 8}}
    fig.layout.polar3["radialaxis"] = {'range': [1938, 1946],
                                       'tickfont': {"size": 8}}
    fig.layout.polar3["angularaxis"] = {'tickfont': {"size": 8}}
    fig.layout.polar4["radialaxis"] = {'range': [1938, 1946],
                                       'tickfont': {"size": 8}}
    fig.layout.polar4["angularaxis"] = {'tickfont': {"size": 8}}
    fig.layout.annotations[0].update(x=0.025)
    fig.layout.annotations[2].update(x=0.025)
    fig.layout.annotations[1].update(x=0.575)
    fig.layout.annotations[3].update(x=0.575)
    fig.update_layout(title_text="A Comparison of Yearly Allied Aircraft Use In Different Theaters of WW2")
    fig.update_layout(coloraxis=dict(colorscale='bluered', showscale=False), showlegend=False)
    fig.add_annotation(text='Color: How often a type of aircraft was used that year compared to other years (Red/Higher -> Blue/Lower) <br>Size: How often a type of aircraft was used that year compared to other types (Larger/More Frequent -> Smaller/Less Frequent)<br>Note: Size indication under 2% use not to scale',
                       align='left',
                       showarrow=False,
                       xref='paper',
                       yref='paper',
                       x=0.5,
                       y=-0.1,
                       bordercolor='black',
                       borderwidth=1)
    fig.show()


def main():

    parse_data()

    plot_data()


if __name__ == "__main__":

    main()
