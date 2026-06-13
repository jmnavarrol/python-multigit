# -*- coding: utf-8 -*-

import errno


class SubrepofileError(Exception):
	'''
	Custom Subrepofile Error Exception.
	
	Raised when subrepos file loading or validation fails.
	
	:param str msg: error message
	:param errno errno: suggested sys.exit errno
	'''
	
	def __init__(self, msg='error while operating subrepo file', errno_val=errno.EINVAL, *args, **kwargs):
		super().__init__(msg, *args, **kwargs)
		self.errno = errno_val
