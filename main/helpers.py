#!/usr/bin/env python
# encoding=utf-8

from functools import wraps

from django.contrib.auth.decorators import user_passes_test
from registration import signals as reg_signals


def group_required(group, login_url=None):
    """
    Decorator for views that checks whether a user has a particular group,
    redirecting to the log-in page if necessary.
    """
    return user_passes_test(lambda u: group in \
                                            [g.name for g in u.groups.all()], \
                            login_url=login_url)


def read_required(login_url=None):
    return user_passes_test(lambda u: 'read' in \
                                            [g.name for g in u.groups.all()], \
                            login_url=login_url)


def write_required(login_url=None):
    return user_passes_test(lambda u: 'write' in \
                                            [g.name for g in u.groups.all()], \
                            login_url=login_url)


def add_read_group_to_new_user(sender, **kwargs):
    from django.contrib.auth.models import Group

    user = kwargs['user']
    read_group = Group.objects.get(name='read')
    user.groups.add(read_group)

reg_signals.user_registered.connect(add_read_group_to_new_user)
