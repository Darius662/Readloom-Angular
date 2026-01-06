#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Calendar UI routes.
Handles calendar-related pages.
"""

from flask import Blueprint, render_template
from frontend.middleware import setup_required

# Create routes blueprint
calendar_routes = Blueprint('calendar_routes', __name__)


@calendar_routes.route('/calendar')
@setup_required
def calendar():
    """Calendar page."""
    return render_template('calendar.html')
