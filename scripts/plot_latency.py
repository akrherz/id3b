"""A flamish graph per 5 March 2022 debacle."""
from zoneinfo import ZoneInfo

import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from pyiem.plot import figure_axes
from pyiem.util import get_sqlalchemy_conn

CST = ZoneInfo("America/Chicago")


def main():
    """Do Things."""
    with get_sqlalchemy_conn("id3b") as conn:
        df = pd.read_sql(
            """
            select valid_at at time zone 'UTC' as valid, wmo_source,
            valid_at - wmo_valid_at as latency from mar5
            WHERE ldm_feedtype = 11 and entered_at > '2022-03-5 13:00'
            and entered_at < '2022-03-5 19:00' and
            extract(minute from wmo_valid_at) > 0 and
            wmo_source not in ('KWAL', 'KWOH', 'KWBC', 'KWNB', 'KWNO', 'KAWN')
            and substr(wmo_source, 1, 1) = 'K'
            and substr(awips_id, 1, 3)
             not in ('RR3', 'HML', 'RR2', 'RRS', 'LSR', 'LLL')
            ORDER by valid ASC
            """,
            conn,
            index_col="valid",
        )
    df["seconds"] = df["latency"] / np.timedelta64(1, "s")
    (fig, ax) = figure_axes(
        title="NWS Text Product Dissemination Latency",
        subtitle=(
            "Based on difference between NOAAPort receipt time "
            "and product WMO valid time."
        ),
        apctx={"_r": "43"},
    )
    ax.scatter(df.index.values, df["seconds"].values, alpha=1)
    # df2 = df[df['wmo_source'] == 'KSGX']
    # ax.scatter(df2.index.values, df2["seconds"].values, alpha=1, color='b')
    df2 = df[df["wmo_source"] == "KDMX"]
    ax.scatter(df2.index.values, df2["seconds"].values, alpha=1, color="r")
    ax.set_ylim(-10, 480)
    ax.set_ylabel("Latency (minutes)")
    ax.set_yticks(np.arange(0, 481, 60))
    ax.set_yticklabels(np.arange(0, 9, 1))
    ax.grid(True)
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%-I %p", tz=CST))
    ax.set_xlim(df.index.values[0], df.index.values[-1])
    ax.set_xlabel("5 March 2022 Central Standard Time")
    fig.text(
        0.05,
        0.02,
        "* Latencies are not exact due to vagaries of how WMO timestamps work"
        ", @akrherz 9 Mar 2022",
    )
    ax.legend(
        handles=[
            Line2D([0], [0], ls="", marker="o", color="b", label="All NWS"),
            Line2D(
                [0], [0], ls="", marker="o", color="r", label="NWS Des Moines"
            ),
        ],
        loc=(0.9, 0.9),
    )
    fig.savefig("test.png")


if __name__ == "__main__":
    main()
