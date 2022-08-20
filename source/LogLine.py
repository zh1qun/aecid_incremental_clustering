#!/usr/bin/python

"""This class describes log lines"""


class LogLine:
    def __init__(self, line_id, line, line_text):
        self.line_id = line_id
        self.line = line
        self.line_text = line_text
        self.cluster = ''
