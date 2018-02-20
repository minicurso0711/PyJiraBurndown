from datetime import timedelta
from datetime import datetime

from dateparser.date import DateDataParser
from jira import JIRA


class JiraHelper:
    def __init__(self, host, user, password):
        self.jira = JIRA(host, basic_auth=(user, password), max_retries=1)
        self.ddp = DateDataParser(languages=['pt', 'en'])

    def get_projects(self):
        return self.jira.projects()

    def get_boards_by_project_key(self, key_project):
        allboards = self.jira.boards(maxResults=1000, type='scrum')
        boards = []
        for board in allboards:
            projects = []
            try:
                projects = board.raw['filter']['queryProjects']['projects']
                for project in projects:
                    if project['key'] == key_project and board.sprintSupportEnabled:
                        boards.append(board)
            except KeyError as e:
                print("\"project\" key not found in the queryProjects' board - Reason: %s" % e)

        return boards

    def get_sprints_by_board_id(self, id_board):
        sprints = self.jira.sprints(id_board, extended=True, maxResults=100)
        return [sprint for sprint in sprints if None != sprints]

    def get_sprint_dates(self, sprint):
        start_date = sprint.raw['startDate']
        end_date = sprint.raw['endDate']
        complete_date = sprint.raw['completeDate']

        dsd = self.ddp.get_date_data(start_date, date_formats=['%d/%b/%y %I:%M %p'])
        dcd = self.ddp.get_date_data(complete_date if 'None' != complete_date else end_date,
                                date_formats=['%d/%b/%y %I:%M %p'])

        return dsd, dcd

    def get_closed_issues_by_sprint(self, sprint_id, start_date, end_date):
        query = "sprint = {0:d} and issuetype not in (Story, Sub-Bug, Sub-Improvement) and status = Done and labels not in (Unplanned)".format(
            sprint_id)
        return self.get_issues_by_jql(query)

    def get_inprogress_issues_by_sprint(self, sprint_id, start_date, end_date):
        query = "sprint = {0:d} and issuetype not in (Story, Sub-Bug, Sub-Improvement) and status != Done and labels not in (Unplanned)".format(
            sprint_id)
        return self.get_issues_by_jql(query)

    def filter_issues_by_label(self, issues, labels):
        items = []
        total = 0.0
        for issue in issues:
            for label in issue.raw['fields']['labels']:
                if label.lower() in [lbl.lower() for lbl in labels]:
                    items.append(issue)
                    total += issue.raw['fields']['customfield_10006']
        return total, items

    def get_issues_by_jql(self, jql):
        issues = self.jira.search_issues(jql, maxResults=500)
        total_points = sum(
            map(lambda s: s.raw['fields']['customfield_10006'] if None != s.raw['fields']['customfield_10006'] else 0.0,
                issues))
        total_test_points, test_issues = self.filter_issues_by_label(issues, ['Test'])
        total_front_points, front_issues = self.filter_issues_by_label(issues, ['Frontend'])
        total_back_issues, back_issues = self.filter_issues_by_label(issues, ['Backend'])
        data = {
            'total_points': float(total_points),
            'issues': issues,
            'total_test_points': total_test_points,
            'test_issues': test_issues,
            'total_front_points': total_front_points,
            'front_issues': front_issues,
            'total_back_points': total_back_issues,
            'back_issues': back_issues
        }
        return data

    def extract_points_series_burned_dayly(self, start_date, end_date, issues, total_points):
        d1 = start_date
        d2 = end_date
        # this will give you a list containing all of the dates
        dd = [d1 + timedelta(days=x) for x in range((d2 - d1).days + 1)]
        average_by_day = round((total_points / len(dd)), 2)
        basic_line = [total_points]
        burned_points_line = [total_points]
        values_burned = [0.0]
        aux = total_points - average_by_day
        burned = total_points
        for actual_date in dd[1:]:
            aux = (aux - average_by_day) if (aux - average_by_day) >= 0.0 else 0.0
            basic_line.append(aux)
            ti_burned_points = self.get_points_burned_by_day(issues, actual_date)
            values_burned.append(ti_burned_points)
            burned = (burned - ti_burned_points) if (burned - ti_burned_points) >= 0.0 else 0.0
            burned_points_line.append(burned)
        # This will convert the dates created by range
        # ddd = [(d1 + timedelta(days=x)).strftime('%d/%m/%Y') for x in range((d2 - d1).days + 1)]
        ddd = [(d1 + timedelta(days=x)) for x in range((d2 - d1).days + 1)]
        return {
            'dates': ddd,
            'basic_line_series': basic_line,
            'burned_line_series': burned_points_line,
            'values_burned': [str(value) for value in values_burned]
        }

    def get_points_burned_by_day(self, issues, actual_date):
        points = 0.0
        for issue in issues:
            # '2017-02-08T07:48:39.000-0200'
            str_date = issue.raw['fields']['updated']
            update_date = self.ddp.get_date_data((str_date.split('T')[0]), date_formats=['%Y-%m-%d'])['date_obj']
            if actual_date.strftime('%d-%m-%Y') == update_date.strftime('%d-%m-%Y'):
                points += issue.raw['fields']['customfield_10006'] if None != issue.raw['fields']['customfield_10006'] else 0.0
        return points
