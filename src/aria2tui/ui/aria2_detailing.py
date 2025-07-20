#!/bin/python
# -*- coding: utf-8 -*-
"""
aria2_detailing.py
Detailings for aria2TUI. 
    - highlights
    - modes

Author: GrimAndGreedy
License: MIT
"""

highlights = [
    {
        "match": "^complete[\s]*$",
        "field": 1,
        "color": 8,
    },
    {
        "match": "^error[\s]*|^removed[\s]*$",
        "field": 1,
        "color": 7,
    },
    {
        "match": "^active[\s]*$",
        "field": 1,
        "color": 9,
    },
    {
        "match": "^waiting[\s]*$",
        "field": 1,
        "color": 11,
    },
    {
        "match": "^paused[\s]*$",
        "field": 1,
        "color": 12,
    },
    { 
        "match": r'^(0\d?(\.\d*)?\b|\b\d(\.\d*)?)\b%?',              # Pattern for numbers from 0 to 20
        "field": 6,
        "color": 7,
    },
    {
        "match": r'^(2\d(\.\d*)?|3\d(\.\d*)?|40(\.\d*)?)(?!\d)\b%?',  # Pattern for numbers from 20 to 40
        "field": 6,
        "color": 11,
    },
    {
        "match": r'^(4\d(\.\d*)?|5\d(\.\d*)?|60(\.\d*)?)(?!\d)\b%?',  # Pattern for numbers from 40 to 60
        "field": 6,
        "color": 9,
    },
    {
        "match": r'^(6\d(\.\d*)?|7\d(\.\d*)?|80(\.\d*)?)(?!\d)\b%?',  # Pattern for numbers from 60 to 80
        "field": 6,
        "color": 9,
    },
    {
        "match": r'^(8\d(\.\d*)?|9\d(\.\d*)?|100(\.\d*)?)(?!\d)\b%?',  # Pattern for numbers from 80 to 100
        "field": 6,
        "color": 8,
    },
]
menu_highlights = [
    {
        "match": "^watch|^view",
        "field": 0,
        "color": 8,
    },
    {
        "match": "^add",
        "field": 0,
        "color": 13,
    },
    {
        "match": "^pause|^remove",
        "field": 0,
        "color": 7,
    },
    {
        "match": "^get",
        "field": 0,
        "color": 22,
    },
    {
        "match": "^edit|^restart",
        "field": 0,
        "color": 10,
    },
    {
        "match": "graph",
        "field": 0,
        "color": 9,
    },
]
modes = [
    {
        'filter': '',
        'sort': 0,
        'name': 'All',
    },
    {
        'filter': '--1 active',
        'name': 'Active',
    },
    {
        'filter': '--1 waiting',
        'name': 'Queue',
    },
    {
        'filter': '--1 waiting|active',
        'name': 'Active+Queue',
    },
    {
        'filter': '--1 paused',
        'name': 'Paused',
    },
    {
        'filter': '--1 complete',
        'name': 'Completed',
    },
    {
        'filter': '--1 error',
        'name': 'Error',
    },
]
operations_highlights = [
    {
        "match": "^pause",
        "field": 0,
        "color": 22,
    },
    {
        "match": "^unpause",
        "field": 0,
        "color": 8,
    },
    {
        "match": "^remove",
        "field": 0,
        "color": 7,
    },
    {
        "match": r"^retry",
        "field": 0,
        "color": 22,
    },
    {
        "match": r"^send to|^change position",
        "field": 0,
        "color": 11,
    },
    {
        "match": r"^change options",
        "field": 0,
        "color": 13,
    },
    {
        "match": "^DL INFO",
        "field": 0,
        "color": 9,
    },
    {
        "match": r"^open",
        "field": 0,
        "color": 10,
    },
    {
        "match": "graph",
        "field": 0,
        "color": 9,
    },
]
