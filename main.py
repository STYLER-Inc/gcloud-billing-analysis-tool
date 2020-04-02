# -*- coding: utf-8 -*-
"""GCP Billing Analysis Tool (G-BAT) (for BigQuery)

This module is written to analyse Google Cloud Platform billing data
that has been exported to billing via the automatic export feature.

It returns data in dictionary format, which then may be used as is or,
for example, converted to JSON to serve other use cases.

Example:
    You must specify the service account location if this is ran outside of
    GCP, i.e. on your local machine.

        $ PROJECT_ID="project-id" \
                DATA_SET="billing-dataset-name" \
                TABLE_NAME="table-name-in-dataset" \
                SLACK_API_TOKEN="your-slack-api-token" \
                GOOGLE_APPLICATION_CREDENTIALS="path-to-creds.json" \
                pipenv run python g-bat.py

    Note that the specified service account key must have access to BigQuery.
    Access to the billing account itself is not required as that is only
    queried via BigQuery.

Attributes:
    SETTINGS: See `settings.py` for more information.
    CLIENT: The BigQuery client.

"""


import calendar

from datetime import date
from typing import Union

from google.cloud import bigquery

from messenger import send_slack_message
from settings import Settings


SETTINGS = Settings()
CLIENT = bigquery.Client()


def get_project_ids() -> list:
    """Gets a list of all project IDs within the billing data from BigQuery.

    Returns:
        Project ID(s)

    """
    query = (
        f"""
        SELECT DISTINCT project.id AS pid
        FROM {SETTINGS.PROJECT_ID}.{SETTINGS.DATA_SET}.{SETTINGS.TABLE_NAME};
        """)
    query_job = CLIENT.query(query)
    return [row.pid for row in query_job.result() if row.pid is not None]


def round_cost_value(cost: float,
                     precision: int = SETTINGS.ROUNDING_PRECISION) -> float:
    """Used to consistently round all cost values to the same format

    Args:
        cost: The cost of which to round.
        precision: The precision with which to round.

    Returns:
        The rounded value.
    """
    return round(cost, precision)


def get_cost_filter_project_daily_interval(project_id: str,
                                           days_ago: int) -> dict:
    """Gets cost data for a specified number of days ago for a specified project.

    Args:
        project_id: The project ID of which to retrieve cost data
        days_ago: The number of days ago from today to retrieve cost data

    Returns:
       Cost data, including currency and date.

    """
    query = (
        f"""
        SELECT
          SUM(cost) as cost,
          currency as currency,
          TIMESTAMP_TRUNC(TIMESTAMP_SUB(
            CURRENT_TIMESTAMP(), INTERVAL {days_ago} DAY),DAY
          ) as date
        FROM {SETTINGS.PROJECT_ID}.{SETTINGS.DATA_SET}.{SETTINGS.TABLE_NAME}
        WHERE
          _PARTITIONTIME BETWEEN TIMESTAMP_TRUNC(TIMESTAMP_SUB(
            CURRENT_TIMESTAMP(), INTERVAL {days_ago} DAY),DAY
          )
          AND TIMESTAMP_TRUNC(TIMESTAMP_SUB(
            CURRENT_TIMESTAMP(), INTERVAL {days_ago} DAY),DAY
          )
          AND project.id='{project_id}'
        GROUP BY currency
        LIMIT 1;
        """)
    query_job = CLIENT.query(query)
    rows_iter = query_job.result(max_results=1)
    rows = list(rows_iter)
    return {
        'cost': round_cost_value(rows[0].cost),
        'currency': rows[0].currency,
        'date': rows[0].date.isoformat()
    }


def get_gcp_daily_total_cost() -> dict:
    """Gets cost data for the past day for all projects.

    Returns:
       Cost data, including currency and date (ISO 8601).

    """
    query = (
        f"""
        SELECT
          SUM(cost) as cost_sum,
          currency as currency,
          DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY) as date,
        FROM {SETTINGS.PROJECT_ID}.{SETTINGS.DATA_SET}.{SETTINGS.TABLE_NAME}
        WHERE
          CAST(DATE(
            _PARTITIONTIME) AS DATE) = DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
        GROUP BY currency
        LIMIT 1;
        """)
    query_job = CLIENT.query(query)
    rows_iter = query_job.result(max_results=1)
    rows = list(rows_iter)
    return {
        'cost_sum': round_cost_value(rows[0].cost_sum),
        'currency': rows[0].currency,
        'date': rows[0].date.isoformat()
    }


def get_gcp_monthly_total_cost() -> dict:
    """Gets cost data for the past month for all projects.

    Returns:
       Cost data, including currency and (month) date (ISO 8601).

    """
    query = (
        f"""
        SELECT
          SUM(cost) as cost_sum,
          currency as currency,
          TIMESTAMP_TRUNC(CURRENT_TIMESTAMP(), MONTH, 'UTC') as month
        FROM {SETTINGS.PROJECT_ID}.{SETTINGS.DATA_SET}.{SETTINGS.TABLE_NAME}
        WHERE
          _PARTITIONTIME BETWEEN TIMESTAMP_TRUNC(
            CURRENT_TIMESTAMP(), MONTH, 'UTC')
          AND TIMESTAMP_TRUNC(CURRENT_TIMESTAMP(), DAY, 'UTC')
        GROUP BY currency
        LIMIT 1;
        """)
    query_job = CLIENT.query(query)
    rows_iter = query_job.result(max_results=1)
    rows = list(rows_iter)
    return {
        'cost_sum': round_cost_value(rows[0].cost_sum),
        'currency': rows[0].currency,
        'date': rows[0].month.isoformat()
    }


def get_gcp_project_daily_top_services(
        project_id: str,
        number: int = SETTINGS.NUMBER_OF_TOP_SERVICES_TO_INVESTIGATE) -> list:
    """Gets data on daily top `number` of the highest costing services on the
    given `project_id`.

    Returns:
       Data on top services and cost

    """
    query = (
        f"""
        SELECT
          SUM(cost) as cost,
          service.description as service_desc,
          currency as currency,
        FROM {SETTINGS.PROJECT_ID}.{SETTINGS.DATA_SET}.{SETTINGS.TABLE_NAME}
        WHERE
          _PARTITIONTIME BETWEEN TIMESTAMP_TRUNC(
            TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR),DAY)
          AND  TIMESTAMP_TRUNC(CURRENT_TIMESTAMP(), DAY)
          AND project.id='{project_id}'
        GROUP BY service_desc, currency
        ORDER BY(cost) DESC
        LIMIT {number};
        """)
    query_job = CLIENT.query(query)
    rows_iter = query_job.result()
    top_services = []
    for row in rows_iter:
        top_services.append({
            'service_name': row['service_desc'],
            'cost': round_cost_value(row['cost']),
            'currency': row['currency']
        })
    return top_services


def get_projected_cost(days_remaining: Union[float, int],
                       total_past_day: float,
                       total_past_month: float) -> float:
    """Calculate the projected cost for the rest of the month.

    Returns:
        Projected cost.
    """
    return total_past_month + (days_remaining * total_past_day)


def get_days_in_month(month: int = date.today().month,
                      year: int = date.today().year) -> int:
    """Gets the days in the specified month.

    Args:
        month: Lookup month.
        year: Lookup year.

    Returns:
        Total days in the specified month.
    """
    return calendar.monthrange(year, month)[1]


def compute_days_remaining_in_present_month(
        days_in_month: int = get_days_in_month()) -> int:
    """Gets the days remaining in the current month.

    Args:
        days_in_month: Total days in the month.

    Returns:
        Number of days remaining in present month.
    """
    return days_in_month - date.today().day


def get_status(
        current_cost: float,
        past_cost: float,
        threshold: Union[int, float] = SETTINGS.WARNING_THRESHOLD_MULTIPLIER) -> str:
    """Intended to determine the status based on two cost values from different
    time periods.

    * If the current cost exceeds the limit, warning status is set.
    * If the current cost is zero, or otherwise, status is considered
    to be nominal.

    Args:
        current_cost: The current, or most recent cost.
        past_cost: The past cost with which to do the comparison.
        threshold: The threshold above the `past_cost` allowed before nominal
            status is no longer nominal.

    Returns:
        The determined status.
    """
    limit = past_cost * threshold
    if (current_cost != 0 and current_cost >= limit and
            current_cost >= SETTINGS.MINIMUM_COST_FOR_WARNING):
        return SETTINGS.STATUS_WARNING
    return SETTINGS.STATUS_NOMINAL


def get_costs(project_ids: list) -> list:
    """Gets costs for the past two days for each project ID in the list.
    The two-day data used to perform a comparison and determine whether the
    project is nominal status or not.

    Args:
        project_ids: One or more GCP project ID(s)

    Returns:
        Cost data for all projects, with the `project_id` as the uppermost key.
    """
    costs = []
    for project_id in get_project_ids():
        one_day_ago = get_cost_filter_project_daily_interval(project_id, 1)
        two_days_ago = get_cost_filter_project_daily_interval(project_id, 2)
        status = get_status(one_day_ago['cost'], two_days_ago['cost'])

        project_costs = {
            'id': project_id,
            'one_day_ago': one_day_ago,
            'two_days_ago': two_days_ago,
            'status': status
        }

        # Get info on highest costing services if `SETTINGS.STATUS_WARNING`
        if status == SETTINGS.STATUS_WARNING:
            project_costs['top_services'] = get_gcp_project_daily_top_services(
                project_id
            )
        costs.append(project_costs)
    return costs


def get_analysis() -> dict:
    """Utilise the methods in this module to perform cost analysis on all GCP
    projects and return that data.

    Returns:
        {
            'breakdown': {
                Cost data for the past two days of each project_id, which also
                includes the status with the `project_id` for each project
                as the uppermost key.
            },
            'summary': {
                Summary for past day, month and projected cost for the entire
                month.
            }
        }

    """
    # Days remaining used to determined projected cost
    past_day = get_gcp_daily_total_cost()
    past_month = get_gcp_monthly_total_cost()
    days_remaining = compute_days_remaining_in_present_month()

    # Get the projected cost
    if past_day['currency'] == past_month['currency']:
        projected_cost_currency = past_day['currency']
    else:
        raise Exception(('Projected cost cannot be calculated without' +
                         'matching currencies'))
    projected_cost = get_projected_cost(days_remaining,
                                        past_day['cost_sum'],
                                        past_month['cost_sum'])

    # Get and sort breakdown based on most expensive cost
    breakdown = get_costs(get_project_ids())
    sorted_breakdown = sorted(
        breakdown,
        key=lambda x: x['one_day_ago']['cost'],
        reverse=True
    )

    return {
        'breakdown': sorted_breakdown,
        'summary': {
            'past_day': past_day,
            'past_month': past_month,
            'projected_cost': {
                'cost': projected_cost,
                'currency': projected_cost_currency
            }
        }
    }


def make_slack_message_section(text: str) -> dict:
    """Generates an object compatiable with Slack's text section.

    Args:
        text: The text to be sent in the message.

    Returns:
        A text section message for delivery via Slack.

    """
    return {
        'type': 'section',
        'text': {
            'type': 'mrkdwn',
            'text': text
        }
    }


def make_slack_message_field_section(fields: list) -> dict:
    """Generates an object compatiable with Slack's text field section.

    Args:
        fields: A list of strigifiable objects. This should be an even
                number since Slack formats fields as two per line,
                generally consisting of key/value pairs.

    Returns:
        A text field section message for delivery via Slack.

    """
    section = {
        'type': 'section',
        'fields': []
    }
    for field in fields:
        section['fields'].append(
            {
                'type': 'mrkdwn',
                'text': str(field)
            }
        )
    return section


def generate_gcp_project_link(project_id: str) -> str:
    """Generates a Slack markdown GCP link from the given `project_id`.

    Args:
        project_id: The project ID of which to hyperlink.

    Returns:
        The generated hyperlink.

    """
    return ('<https://console.cloud.google.com/home/' +
            f'dashboard?project={project_id}|{project_id}>')


def format_project_title(rank: int, project_id: str, status: str) -> str:
    """Formats a project title for display in Slack.

    Args:
        rank: The rank of in the list. Will be prepended to the title.
        project_id: The project ID.
        status: The status of the project. This is used to determine which
                emoji is used to prefix the title string.

    Returns:
        A formatted title string.

    """
    project_link = generate_gcp_project_link(project_id)
    if status == SETTINGS.STATUS_WARNING:
        return f':warning: *{rank}. {project_link}*'
    return f':white_check_mark: *{rank}. {project_link}*'


def make_slack_message_divider() -> dict:
    """Generates a simple divider for a Slack message.

    Returns:
        The generated divider.

    """
    return {'type': 'divider'}


def send_project_ranking_line_to_slack(rank: int, project_data: dict) -> None:
    """ Sends a ranking message line to Slack.

    Args:
        rank: The number in the ranking.
        project_data: The data for the project.

    Returns:
        None

    """
    title = format_project_title(rank,
                                 project_data['id'],
                                 project_data['status'])
    past_day = (f"{project_data['one_day_ago']['cost']} " +
                f"{project_data['one_day_ago']['currency']}")
    send_slack_message(blocks=[
        make_slack_message_field_section(
            [
                title,
                past_day
            ]
        )
    ])


def send_project_top_services_to_slack(project_id: str,
                                       top_services: list) -> None:
    """ Sends a project's top services to Slack.

    Args:
        rank: The number in the ranking.
        project_data: The data for the project.

    Returns:
        None

    """
    send_slack_message(
        blocks=[make_slack_message_section(
            f"*Top Services for {project_id}*:")])
    for service in top_services:
        send_slack_message(blocks=[
            make_slack_message_field_section(
                [
                    f"- {service['service_name']}",
                    f"{service['cost']} {service['currency']}"
                ]
            )
        ])


def prepare_summary_line(cost: float, currency: str) -> str:
    """Prepares a summary line by formatting it.

    Args:
        cost: The cost of the summary line item.
        currency: The currency to append to the summary line item.

    Returns:
        The formatted summary line.

    """
    return (f'{cost} {currency}')


def send_summary_to_slack(summary_data: dict) -> None:
    """Prepares and sends summary data to Slack.

    Args:
        summary_data: Contains summary datastructure.

    Returns:
        None

    """
    # Summary Section
    total_past_day = prepare_summary_line(
        summary_data['past_day']['cost_sum'],
        summary_data['past_day']['currency']
    )
    total_past_month = prepare_summary_line(
        summary_data['past_month']['cost_sum'],
        summary_data['past_month']['currency']
    )
    projected_cost = prepare_summary_line(
        summary_data['projected_cost']['cost'],
        summary_data['projected_cost']['currency']
    )
    send_slack_message(blocks=[make_slack_message_section('*Summary*')])
    send_slack_message(blocks=[
        make_slack_message_field_section(
            [
                'Total Past Day:', total_past_day,
                'Total Past Month:', total_past_month,
                'Projected Cost:', projected_cost
            ]
        )
    ])


def slack_notify() -> None:
    """Prepares analysis data and sends it to Slack.

    Returns:
        None

    """
    analysis_data = get_analysis()

    # Base Message
    base_message = [
        {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': '*Daily Billing Analysis Report*',
            },
        },
    ]
    base_message.append(make_slack_message_divider())
    send_slack_message(blocks=base_message)

    # Send project ranking line to Slack
    for rank, project_data in enumerate(analysis_data['breakdown'], start=1):
        send_project_ranking_line_to_slack(rank, project_data)

        # Send top services if given
        if 'top_services' in project_data.keys():
            send_project_top_services_to_slack(
                project_data['id'],
                project_data['top_services'])

    # Prepare and send trailing overally summary
    send_slack_message(blocks=[make_slack_message_divider()])
    send_summary_to_slack(analysis_data['summary'])


if __name__ == '__main__':
    slack_notify()
