
import numpy as np

import os

from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


class PlotlyHelper:

    def generate_burndown_graph_file(self, data, title, filename):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        plt.rcParams["figure.figsize"] = (20,10)
        pp = PdfPages(filename + ".pdf")
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator())
        plt.plot(np.array(data['dates']), np.array(data['basic_line_series']), color='k', label='Guideline')
        plt.plot(np.array(data['dates']), np.array(data['burned_line_series']), marker='o', color='r', label='Remaining Values')
        for a, b in zip(data['dates'], data['burned_line_series']):
            plt.text(a, b, str(b), ha='left', va='bottom', rotation=-45, fontweight='bold')
        plt.gcf().autofmt_xdate()
        plt.xlabel('Sprint Dates')
        plt.ylabel('Story Points')
        plt.xticks(rotation=90)
        plt.title(title)
        plt.legend(loc='best')
        plt.grid(True)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        plt.savefig(pp, format='pdf')
        pp.close()
        plt.clf()