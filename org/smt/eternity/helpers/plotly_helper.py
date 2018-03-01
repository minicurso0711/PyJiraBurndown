import numpy as np

import os

from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


class PlotlyHelper:
    def generate_burndown_graph_file(self, data, title, filename):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        plt.rcParams["figure.figsize"] = (30, 15)
        pp = PdfPages(filename + ".pdf")
        for i in range(0, len(data)):
            ax = plt.subplot(221 + i)
            self.generate_subplot_graph(data[i], title[i], i not in (0, 1))
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        plt.savefig(pp, format='pdf')
        pp.close()
        plt.clf()

    def generate_subplot_graph(self, data, title, show_x_label):
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%y'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator())
        timetuple = [mdates.date2num(d) for d in data['dates']]
        plt.plot(np.array((timetuple[0], timetuple[-1])), np.array((data['basic_line_series'][0], data['basic_line_series'][-1])), color='k', label='Guideline')
        plt.plot(np.array(timetuple), np.array(data['burned_line_series']), marker='o', color='r',
                 label='Remaining Values')
        for a, b in zip(timetuple, data['burned_line_series']):
            plt.text(a, b, str(b), ha='center', va='bottom', rotation=-45, fontweight='bold')
        if show_x_label:
            plt.xlabel('Sprint Dates')
        plt.ylabel('Story Points')
        plt.tight_layout(w_pad=0.3)
        plt.xticks(timetuple, rotation=90)
        plt.gca().set_xlim(timetuple[0], timetuple[-1])
        plt.gca().set_ylim(data['basic_line_series'][-1] - 5, data['basic_line_series'][0] + 5)
        plt.title(title)
        plt.legend(loc='best')
        plt.grid(True)
