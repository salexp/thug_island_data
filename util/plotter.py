try:
    import matplotlib.patheffects as path_effects
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker
    from matplotlib import dates
    from matplotlib.font_manager import FontProperties
except ImportError:
    print "Install matplotlib (>pip install matplotlib) before continuing..."
    exit()


color_sequence = ['#1f77b4', '#ff7f0e', '#ffbb78', '#2ca02c', '#d62728', '#ff9896',
                  '#9467bd', '#c49c94', '#7f7f7f', '#17becf', '#9edae5']
# http://matplotlib.org/examples/showcase/bachelors_degrees_by_gender.html


def owner_color(owner):
    lst = sorted(owner.league.owners.keys())
    ind = lst.index(owner.name)
    return color_sequence[ind]


def computer_rankings(league):
    mx = 0.0
    fig, ax = plt.subplots(figsize=(14, 7))
    week = league.current_week
    power_rankings = league.power_rankings
    owners = [p[0] for p in power_rankings[week]]
    owner_ranks = {}
    for owner in owners:
        lo = league.owners[owner]
        owner_ranks[owner] = []
        for i in range(2, int(week)):
            owner_ranks[owner].append(league.rankings[i].ranks[owner])

        x = [i+1 for i in range(2, int(week))]
        y = [10-r for r in owner_ranks[owner]]

        # Plot line
        ax.plot(x, y, 'o-', lw=1.5, color=owner_color(lo))
        plt.text(x[-1] + 0.1, y[-1], owner, color=owner_color(lo), fontsize=14)

    # Format axis
    plt.xlim(3, min([x[-1]+2.5, 13]))
    plt.ylim(0.5, 10.5)
    plt.xticks(range(3, 14), fontsize=12)
    plt.yticks(range(1, 11), [10-r for r in range(11)], fontsize=12)

    # Format edges
    ax.yaxis.grid(True, 'major')
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()

    # Add axis labels and titel
    plt.xlabel("Week", fontsize=16)
    plt.ylabel("Computer Rank", fontsize=16)

    # plt.show()
    plt.savefig("computer_rankings", bbox_inches='tight')
