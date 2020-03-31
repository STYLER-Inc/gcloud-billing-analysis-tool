# -*- coding: utf-8 -*-
"""GCP Billing Analysis Tool (G-BAT) Settings

Attributes:
    *** ↓ Required ↓ ***

    Settings.PROJECT_ID (str): GCP Project ID where BigQuery table is hosted
    Settings.DATA_SET (str): BigQuery dataset where billing data is exported
    Settings.TABLE_NAME(str): Name of the table within the dataset
    Settings.SLACK_CHANNEL (str): Slack channel to send alerts to
    Settings.SLACK_API_TOKEN (str): API token for sending Slack alerts

    *** ↑ Required ↑ ***

    Settings.MINIMUM_COST_FOR_WARNING(str): Sets the minimum cost at which a
        warning can be issued. Any costs that would trigger warnings
        below this level are ignored.

    Settings.ROUNDING_PRECISION (int): Number of decimal places with which to
    round currency values.

    Settings.WARNING_THRESHOLD_MULTIPLIER (int/float): Used in `get_status()`
        to set the limit to determine whether the status should be
        `Settings.STATUS_WARNING` or `Settings.STATUS_NOMINAL`.

    Settings.NUMBER_OF_TOP_SERVICES_TO_INVESTIGATE (int): The number of top
        costing services for the last day to investigate if the
        project status is `Settings.STATUS_WARNING`.

    Settings.STATUS_WARNING (str): Text to use for warning status

    Settings.STATUS_NOMINAL (str): Text to use for nominal status

"""

import os


class Settings:
    # Default Settings
    MINIMUM_COST_FOR_WARNING = 10
    ROUNDING_PRECISION = 2
    WARNING_THRESHOLD_MULTIPLIER = 2
    NUMBER_OF_TOP_SERVICES_TO_INVESTIGATE = 5
    STATUS_WARNING = 'WARNING'
    STATUS_NOMINAL = 'NOMINAL'

    def __init__(self):
        if 'PROJECT_ID' in os.environ:
            self.PROJECT_ID = os.environ['PROJECT_ID']
        else:
            raise Exception('Must specify PROJECT_ID') 
        
        # Required
        if 'DATA_SET' in os.environ:
            self.DATA_SET = os.environ['DATA_SET']
        else:
            raise Exception('Must specify DATA_SET') 

        if 'TABLE_NAME' in os.environ:
            self.TABLE_NAME = os.environ['TABLE_NAME']
        else:
            raise Exception('Must specify TABLE_NAME') 

        if 'SLACK_CHANNEL' in os.environ:
            self.SLACK_CHANNEL = os.environ['SLACK_CHANNEL']
        else:
            raise Exception('Must specify SLACK_CHANNEL') 

        if 'SLACK_API_TOKEN' in os.environ:
            self.SLACK_API_TOKEN = os.environ['SLACK_API_TOKEN']
        else:
            raise Exception('Must specify SLACK_API_TOKEN') 

        # General Settings
        if 'MINIMUM_COST_FOR_WARNING' in os.environ:
            self.MINIMUM_COST_FOR_WARNING = os.environ['MINIMUM_COST_FOR_WARNING']

        if 'ROUNDING_PRECISION' in os.environ:
            self.ROUNDING_PRECISION = os.environ['ROUNDING_PRECISION']

        if 'WARNING_THRESHOLD_MULTIPLIER' in os.environ:
            self.WARNING_THRESHOLD_MULTIPLIER = os.environ[
                'WARNING_THRESHOLD_MULTIPLIER']

        if 'NUMBER_OF_TOP_SERVICES_TO_INVESTIGATE' in os.environ:
            self.NUMBER_OF_TOP_SERVICES_TO_INVESTIGATE = os.environ[
                'NUMBER_OF_TOP_SERVICES_TO_INVESTIGATE']

        if 'STATUS_WARNING' in os.environ:
            self.STATUS_WARNING = os.environ['STATUS_WARNING']

        if 'STATUS_NOMINAL' in os.environ:
            self.STATUS_NOMINAL = os.environ['STATUS_NOMINAL']
