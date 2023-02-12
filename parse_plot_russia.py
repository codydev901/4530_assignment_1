import pandas as pd
import matplotlib.pyplot as plt

"""
Doc Doc Doc
"""

# Some helper stuff for parse_data
DOW = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
DOW_LU = {i: v for i, v in enumerate(DOW)}
ORDER_LU = {v: i for i, v in enumerate(DOW)}


def parse_data():

    # Load in Raw Data
    per_df_raw = pd.read_csv("raw_data/russia_losses_personnel.csv")

    # Take a look at it
    print("Raw Personnel Losses")
    print(per_df_raw.head())
    print(per_df_raw.info())

    # Since Personnel Losses appear be an incrementing sum total,
    # need to get a diff between i and i+1.
    per_df_parsed = per_df_raw[["date", "personnel"]].copy()  # Limit to only attributes of interested
    per_df_parsed["daily_loss"] = per_df_parsed["personnel"].diff()  # Calc the Diff
    per_df_parsed["daily_loss"].loc[0] = per_df_parsed["personnel"].loc[0]  # Handle NaN at first index
    per_df_parsed["daily_loss"] = per_df_parsed["daily_loss"].astype(int)  # Change back it Int type

    print("Check Personnel Loss Daily")
    print(per_df_parsed.head())
    print(per_df_parsed.tail())

    # Now Lets Convert Date to Day of the Week
    per_df_parsed["date_obj"] = pd.to_datetime(per_df_parsed["date"])  # Convert date str to obj
    per_df_parsed["day_of_week"] = per_df_parsed["date_obj"].apply(lambda x: DOW_LU[x.dayofweek])

    print("Check Personnel Loss Day of Week")
    print(per_df_parsed.head())
    print(per_df_parsed.tail())

    # So I want to look at each week individually and simply determine which
    # day was the most dangerous that week. Will end up with ~50 items or so,
    # each representing a week of the war and which day was the most dangerous that week

    # Discard 2022-25-02 -> 2022-27-02 (Discussed in Paper), luckily data ends on a Sunday
    per_df_parsed = per_df_parsed.drop([0, 1, 2])

    dd_df = [["week_of_war", "dangerous_day_of_week"]]

    # Probably cleaner way to do this, but this is clear.
    week_count = 0
    worst_day = None
    worst_losses = 0
    for i, row in per_df_parsed.iterrows():
        # New Week
        if worst_day and row["day_of_week"] == "Monday":
            dd_df.append([week_count, worst_day])
            worst_day = None
            worst_losses = 0
            week_count += 1
        # Determine Most Dangerous During Week
        if row["daily_loss"] > worst_losses:
            worst_day = row["day_of_week"]
            worst_losses = row["daily_loss"]

    # Convert "Dangerous Day" (dd_df) to DataFrame
    dd_df = pd.DataFrame(data=dd_df[1:], columns=dd_df[0])
    print("Dangerous Day DF")
    print(dd_df.head())
    print(dd_df.info())

    # Lets Spot Check A Little
    print("Spot Check Daily Loss vs Dangerous Day of Week")
    for i, row in list(per_df_parsed.iterrows())[:21]:
        print(row["date"], row["day_of_week"], row["daily_loss"])

    # Count by day
    dd_counts = dd_df.groupby("dangerous_day_of_week")["dangerous_day_of_week"].count()
    print(dd_counts)

    # Convert Series Obj to DF for Write
    final_df = [["day_of_week", "weeks_most_dangerous"]]
    for v in dd_counts.items():
        final_df.append([v[0], v[1]])

    # Write out
    final_df = pd.DataFrame(data=final_df[1:], columns=final_df[0])
    # Sort to make cleaner later for graphing
    final_df["week_order"] = final_df["day_of_week"].apply(lambda x: ORDER_LU[x])
    final_df = final_df.sort_values(by=["week_order"])
    print(final_df.head())
    final_df.to_csv("parsed_data/rus_dd_week_parsed.csv", index=False)


def plot_data():

    df = pd.read_csv("parsed_data/rus_dd_week_parsed.csv")

    plt.bar(x=df["day_of_week"], height=df["weeks_most_dangerous"])

    plt.xlabel("Day of Week")
    plt.ylabel("Weeks Highest Losses")
    plt.title("Weekly Highest Personnel Losses By Day of Week For Russia in the Ukraine War")

    plt.show()


def main():

    parse_data()

    plot_data()


if __name__ == "__main__":

    main()
