from org.smt.eternity.helpers.jira_helper import JiraHelper
from org.smt.eternity.helpers.plotly_helper import PlotlyHelper
import configparser
import os

def load_properties():
    config = configparser.ConfigParser()
    config._interpolation = configparser.ExtendedInterpolation()
    config.read('./resources/config.properties')
    return config

def set_config_proxy(config):
    status = config['proxy.config']['enabled'] == 'True'
    if status:
        os.environ["HTTP_PROXY"] = config['proxy.config']['http_proxy']
        os.environ["HTTPS_PROXY"] = config['proxy.config']['https_proxy']

def print_menu(items, text_items):
    option = len(items)
    while option >= len(items):
        for i in range(0, len(items)):
            print("{} - {}".format(str(i), items[i].raw['name']))
        try:
            option = int(input("Select the " + text_items + ":"))
        except Exception as e:
            continue
    return items[option]

if __name__ == '__main__':
    config = load_properties()
    set_config_proxy(config)
    jhelper = JiraHelper(config['jira.config']['host'], config['jira.config']['username'], config['jira.config']['password'])
    phelper = PlotlyHelper()
    dates = []
    project = print_menu(jhelper.get_projects(), 'project')
    board = print_menu(jhelper.get_boards_by_project_key(project.key), 'board')
    sprint = print_menu(jhelper.get_sprints_by_board_id(board.id), 'sprint')
    try:
        dates = jhelper.get_sprint_dates(sprint)
        start_date = dates[0]['date_obj']
        end_date = dates[1]['date_obj']
        data_closed = jhelper.get_closed_issues_by_sprint(sprint.id,
                                                          start_date.strftime('%Y-%m-%d %H:%M'),
                                                          end_date.strftime('%Y-%m-%d %H:%M'))
        data_opened = jhelper.get_inprogress_issues_by_sprint(sprint.id,
                                                              start_date.strftime('%Y-%m-%d %H:%M'),
                                                              end_date.strftime('%Y-%m-%d %H:%M'))
        general_graph_data = jhelper.extract_points_series_burned_dayly(start_date, end_date, data_closed['issues'],
                                                                        (data_closed['total_points'] + data_opened['total_points']))
        test_graph_data = jhelper.extract_points_series_burned_dayly(start_date, end_date, data_closed['test_issues'],
                                                                     (data_closed['total_test_points'] + data_opened['total_test_points']))
        front_graph_data = jhelper.extract_points_series_burned_dayly(start_date, end_date, data_closed['front_issues'],
                                                                      (data_closed['total_front_points'] + data_opened['total_front_points']))
        back_graph_data = jhelper.extract_points_series_burned_dayly(start_date, end_date, data_closed['back_issues'],
                                                                     (data_closed['total_back_points'] + data_opened['total_back_points']))

        # Generate Bundown Graphs
        prefix_burndown_title = "{} - {} - ".format(project.name, sprint.name)
        prefix_filename = './images/#/#'.replace('#', sprint.name.replace(' ','').lower())
        phelper.generate_burndown_graph_file(general_graph_data, prefix_burndown_title + 'General',
                                             prefix_filename + '_general')
        phelper.generate_burndown_graph_file(test_graph_data, prefix_burndown_title + 'Test',
                                             prefix_filename + '_test')
        phelper.generate_burndown_graph_file(front_graph_data, prefix_burndown_title + 'FrontEnd',
                                             prefix_filename + '_frontend')
        phelper.generate_burndown_graph_file(back_graph_data, prefix_burndown_title + 'BackEnd',
                                             prefix_filename + '_backend')
    except Exception as e:
        print('An error occurring during the process...')
        print(e)