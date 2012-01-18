# Copyright 2012, Alex Light.
#
# This file is part of Reddit background updater (RBU).
#
# RBU is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# RBU is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with RBU.  If not, see <http://www.gnu.org/licenses/>.
#

    
import re
from .._exceptions import Unsuitable

_regex_type = type(re.compile(''))

def requires_runtime_checking(check_func):
    """
    Use this to decorate functions where the function needs information it only gets at runtime
    determine if it can be used. the argument should be a function that takes in both the
    configuration object and the child and returns true if the decorated function can be used
    and false if it cannot.
    """
    def wraper(func):
	def out(conf, child):
	    if check_func(conf, child):
		func(conf, child)
	    else:
		raise Unsuitable()
	out._runtime_check = True
	out.__doc__ = func.__doc__
	if hasattr(func, 'acceptable'):
	    out.acceptable = func.acceptable
	    return out
	else:
	    out.acceptable = lambda a: True
	    return out
    return wraper

def requires_URL(url):
    """
    a decorator that is given either a regex or a string and 
    puts the is_suitable attribute on the given function.
    this attribute is a function that will return true when the 
    the url attribute on the reddit post matches all of the 
    domains set to be required.
    """
    if isinstance(url, _regex_type):
	match = lambda dmn: url.search(dmn['data']['url']) is not None
    else:
	match = lambda dmn: url == dmn['data']['url']
    def dec(func):
	if hasattr(func, 'acceptable'):
	    other_dmn = func.acceptable
#that its still here means that it already has a domain requirement
	    func.acceptable = lambda child: match(child) and other_dmn(child)
	else:
	    func.is_suitable = match
	return func	
    return dec 

def requires_domain(domain):
    """
    a decorator that is given either a regex or a string and 
    puts the is_suitable attribute on the given function.
    this attribute is a function that will return true when the 
    the domain attribute on the reddit post matches all of the 
    domains set to be required.
    """
    if isinstance(domain, _regex_type):
	match = lambda child: domain.search(child['data']['domain']) is not None
    else:
	match = lambda child: domain == child['data']['domain']
    def dec(func):
	if hasattr(func, 'acceptable'):
	    other_dmn = func.acceptable
#that its still here means that it already has a domain requirement
	    func.acceptable = lambda dmn: match(dmn) and other_dmn(dmn)
	else:
	    func.acceptable = match
	return func	 
    return dec

def priority(num):
    """
    takes in a number and a function and decorates the function so that it
    has that priority.
    """
    def wrapper(func):
	func.priority = num
	return func
    return wrapper


