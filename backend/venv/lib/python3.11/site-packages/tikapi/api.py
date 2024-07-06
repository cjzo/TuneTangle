#/usr/bin/python3

#############################
#  Made with Rests          #
#  github.com/el1s7/rests   #
#############################

'''
	API
'''
from typing import Callable
import requests
import re
import sys         
import warnings
import traceback

warnings.filterwarnings("ignore")

class APIResponse(requests.Response):

	def next_items(self) -> 'APIResponse':
		'''
			A convenient method to get the next batch of items, if the endpoint has iteration parameters (e.g cursor)
		'''
		pass

	def save_video(self, link: str, path: str, **requestKwargs):
		'''
			A method for downloading and saving videos.
		'''
		pass

class APIException(Exception):
	pass

class ValidationException(Exception):
	field: str = None
	pass

class ResponseException(APIException):
	response: APIResponse = None
	pass


def get_full_class_name(obj):
    module = obj.__class__.__module__
    if module is None or module == str.__class__.__module__:
        return obj.__class__.__name__
    return module + '.' + obj.__class__.__name__

def exception_handler(exception_type, exception, tb, original=sys.excepthook):
	'''
		Hide ugly lines from exceptions
	'''
	if not isinstance(exception, APIException):
		return original(exception_type, exception, traceback)
	
	errors = traceback.format_tb(tb)
	clean_errors = [
		"Traceback (most recent call last):\n"
	]
	for error in errors:
		#  "on_error\n    raise exception" in error
		if "wrap({" in error or "current_options.get('on_error')" in error:
			continue
		clean_errors.append(error)
		
	full_error_name = get_full_class_name(exception)

	clean_errors.append(f"\n{full_error_name}: {exception}")

	print(''.join(clean_errors))
	
	return False
	
sys.excepthook = exception_handler

class Default:
	'''
		Store function default args and distinguish between explicit args
	'''
	def __repr__(self):
		return str(self.value)
	
	def __init__(self, value):
		self.value = value


def make_request(url, method, requests_kwargs) -> requests.Response:
	return getattr(requests, method)(url, verify=False, **requests_kwargs)

def copy_options(o: dict): 
	o = o or {}
	return {
		**o,
		'params': {
			**o.get('params', {})
		},
		'values': {
			**o.get('values', {})
		},
		'headers': {
			**o.get('headers', {})
		},
	}

def parse_set(values: dict):

	if not isinstance(values, dict):
		raise APIException("Invalid __options__ object.")
	
	store_options = copy_options(values.get("__options__", {}))

	if values.get("__options__"):
		del values["__options__"]
	
	for key, value in list(values.items()):
		if (value is None):
			del values[key]
	
	return {
		**store_options,
		'values':{
			**store_options.get('values',{}),
			**values
		}
	}

def merge_options(prev: dict, current: dict, mutate=False):

	first_options = (prev or copy_options({})) if mutate else copy_options(prev)

	second_options = copy_options(current)

	second_options['headers'] = {
		**first_options['headers'],
		**second_options['headers']
		
	}

	second_options['params'] = {
		**first_options['params'],
		**second_options['params']
	}

	second_options['values'] = {
		**first_options['values'],
		**second_options['values']
	}
	
	first_options.update(second_options)

	return first_options


def get_one(*args):
	'''
		Return a value that is not None
	'''
	for arg in args:
		if arg is not None:
			return arg
	
	return None

def Rests(options: dict):
	
	global_options = {"base":"https://api.tikapi.io","sandboxBase":"http://sandbox.tikapi.io","headers":{"User-Agent":"Rests Python (v1.0.6)"},"params":{"apiKey":{"name":"X-API-KEY","required":True,"location":"headers","validate":"^[a-zA-Z0-9]{10,}$","example":"DemoAPIKeyTokenSeHYGXDfd4SFD320Sc39Asd0Sc39Asd4s","help":"The TikAPI API Key is required for all requests","$initsOnly":True}},"values":{},"on_error":None,"on_success":None,"on_request":None,"proxies":None,"__$root__":"API","$other":{"openapi":{"packageName":"tikapi","fields":{"security":[{"apiKey":[]}],"responses":{"403":{"$ref":"./error_responses/403.yaml"}},"parameters":[]}}}}

	merge_options(global_options, (options or {}), True)

	encoding_map = {
		"json": "json",
		"form": "data",
		"urlencoded": "data",
	}

	allowed_param_locations = ["headers", "body", "query", "path"]

	def_param_locations = {
		'post': 'body',
		'get': 'query',
	}

	type_map = {
		'str': 'string',
		'int': 'number',
		'float': 'number',
		'bool': 'boolean',
		'list': 'array',
		'tuple': 'array',
		'dict': 'object'
	}

	def wrap(request:dict, category_options: dict=None, category_key: str= None) -> Callable[[dict], APIResponse]:
			request['method'] = request.get('method','get').lower()
			request['params'] = request.get('params', {})
			bound_options = category_options

			def process_request(**params):

				current_options = merge_options(global_options, bound_options)

				current_options['on_request'] = request.get('on_request',current_options.get('on_request'))
				current_options['on_success'] = request.get('on_success',current_options.get('on_success'))
				current_options['on_error'] = request.get('on_error',current_options.get('on_error'))

				url = f"{current_options.get('base','')}{request.get('path','')}"
				
				is_sandbox = (params and params.get('__sandbox__')) or (current_options and current_options.get('values',{}).get('__sandbox__'))

				if is_sandbox:
					url = f"{current_options.get('sandboxBase',current_options.get('base',''))}{request.get('path','')}"

				options = {
					"method": request['method'],
					"headers": {**current_options.get('headers')},
					"proxies": current_options.get('proxies'),
				}

				body_type = encoding_map.get(request.get("enctype"), "json")

				body_store = {}
				query_store = {}

				request_params = {**current_options.get('params',{}), **request.get("params",{})}

				for param_name, param in request_params.items():

					current_param_value = params.get(param_name)
					default_param_value = param.get("default")
					options_param_value = current_options.get('values',{}).get(param_name)
					example_param_value = param.get("example") if is_sandbox else None

					param_value = get_one(
						current_param_value, 
						options_param_value,
						example_param_value,
						default_param_value, 
					)
					
					param_dest = param.get("name") or param_name
					param_error = param.get("help") or f"The '{param_name}' field is invalid."

					exception = ValidationException(param_error)
					exception.field = param_name

					if param.get("required") and param_value is None:
						raise exception from None

					elif param_value is None:
						continue

					if param.get("format") and callable(param.get("format")):
						try:
							param_value = param["format"](param_value)
						except Exception as e:
							exception = ValidationException(e.args[0] or param_error)
							exception.field = param_name
							raise exception from None

					if param.get("type") and param["type"] != "any":
						if (
							(
								type_map.get(type(param_value).__name__) != param['type']
							)
						):
							raise exception from None

					if param.get("validate") and not re.match(param["validate"], str(param_value)):
						raise exception from None


					if param.get("type") == "number":
						if "max" in param and int(param_value) > int(param["max"]):
							exception = ValidationException(f"The maximum allowed value for the {param_dest} parameter is {param['max']}")
							exception.field = param_name
							raise exception from None

						if "min" in param and int(param_value) < int(param["min"]):
							exception = ValidationException(f"The minimum allowed value for the {param_dest} parameter is {param['min']}")
							exception.field = param_name
							raise exception from None

					if param.get("in") and isinstance(param["in"], list) and param_value not in param["in"]:
						exception = ValidationException(f"The {param_dest} parameter should be one of these values: {', '.join(param['in'])}")
						exception.field = param_name
						raise exception from None

					param_location = (
						param.get("location")
						if type(param.get("location")) == str
						else def_param_locations[options["method"]]
					)

					if param_location not in allowed_param_locations:
						exception = ValidationException(f"Invalid location for '{param_name}' field.")
						exception.field = param_name
						raise exception from None

					if param_location == "headers":
						options["headers"] = options.get("headers", {})
						options["headers"][param_dest] = param_value
						continue

					if param_location == "body":
						body_store[param_dest] = param_value
						continue

					if param_location == "query":
						query_store[param_dest] = param_value
						continue

					if param_location == "path":
						url = url.replace("{{{}}}".format(re.escape(param_dest)), str(param_value))


				options['body'] = body_store
				options['query'] = query_store
				options['encoding'] = body_type

				request_info = {
					'url': url, 
					'options': options, 
					'params': params,
					'key': category_key,
					'instance': Rests,
					'self': wrap(request, category_options, category_key)
				}

				if(callable(current_options.get('on_request'))):

					requestCallbackRes = current_options.on_request(request_info)

					if(requestCallbackRes):
						returnsUrl = (isinstance(requestCallbackRes, dict) and requestCallbackRes.get('url'))
						returnsOptions = (isinstance(requestCallbackRes, dict) and requestCallbackRes.get('options'))

						if not returnsUrl or returnsOptions:
							return requestCallbackRes
						
						if(returnsUrl):
							url = requestCallbackRes.get('url')
							request_info['url'] = url

						if(returnsOptions):
							options =  requestCallbackRes.get('options')
							request_info['options'] = options

					if(requestCallbackRes == False):
						return False

				requests_kwargs = {
					'headers': options.get('headers', {}),
					'proxies': options.get('proxies', None)
				}

				if(len(options['body'])):
					requests_kwargs[options['encoding']] = options['body']

				if(len(options['query'])):
					requests_kwargs['params'] = options['query']

				try:
					response = make_request(url, options['method'], requests_kwargs)
					response.raise_for_status()

					if(callable(current_options.get('on_success'))):
						successCallbackRes = current_options.get('on_success')(response, request_info)
						if(successCallbackRes != None):
							return successCallbackRes

					return response

				except requests.HTTPError as e:
					exception = ResponseException(e)
					exception.response = e.response

				except Exception as e:
					exception = e
					
				if(callable(current_options.get('on_error'))):
					errorCallbackRes = current_options.get('on_error')(exception, request_info)
					if(errorCallbackRes != None):
						return errorCallbackRes

				raise exception

			return process_request


	class BaseClass:

		__options__ = {}

		def __new__(cls, **values) -> 'BaseClass':

			if global_options.get('__$root__') == cls.__name__:
				raise APIException("This is already initialized, you can use 'set' instead.")

			currentOptions = merge_options(global_options, cls.__get_options__())

			updateOptions = parse_set(values)

			newOptions = merge_options(currentOptions, updateOptions)

			newObject = Rests({
				**newOptions,
				"__$root__": cls.__name__
			})

			newMe = getattr(newObject.__Rests__, cls.__name__)

			return newMe

		@classmethod
		def set(cls, **values) -> 'BaseClass':
			'''
				Update values
			'''
			if global_options.get('__$root__') != cls.__name__:
				raise APIException("You can only call set on initialized roots.")
		
			merge_options(global_options, parse_set(values), True)
		
			return cls
		
		@classmethod
		def __get_options__(cls):
			if global_options.get('__$root__') == cls.__name__:
				return global_options
			else:
				return cls.__options__

	
	Rests.BaseClass = BaseClass
	class Public(Rests.BaseClass):
		'''
			Public Endpoints Category 
		'''

		__options__ = {"headers":{},"params":{"country":{"type":"string","validate":"^[a-z]{2}$","help":"You can optionally choose the proxy country from where the request\n\t\t\t\t\tis being sent by providing an ISO Code (e.g us, ca, gb) — 200+ countries supported","location":"query","example":"us"},"session_id":{"type":"number","max":100,"example":0,"help":"(Optional) Longer sessions. The cookies and IP are preserved through different requests for a longer amount of time. You should include this in order to get different posts on every request."}},"values":{},"$other":{"openapi":{"fields":{"tags":["Public"],"parameters":[],"responses":{}}}}}

		def __new__(self, country: str = None, session_id: int = None, **values) -> 'Public':
			'''
				Initialize new 'Public' instance with default values & options
			'''
			return super().__new__(self, country=country, session_id=session_id, **values)

		@classmethod
		def set(self, country: str = None, session_id: int = None, **values) -> 'Public':
			'''
				Method is only available for the root category.
				Set default values & options for 'Public'
			'''
			return super().set(country=country, session_id=session_id, **values)
	
		@classmethod
		def check(cls, username: str = None, user_id: str = None, country: str = None, session_id: int = None, **otherParams) -> APIResponse:
			'''
				Get a user's profile information 
			'''
			
			return wrap({"path":"/public/check","help":"Get a user's profile information","comment":"Get profile information and statistics from a username.","params":{"username":{"help":"The TikTok user username","validate":"^([a-zA-Z0-9_.]+|https?://vm.tiktok.com/[a-zA-Z0-9]+/?)$","type":"string","example":"lilyachty"},"user_id":{"help":"Optionally you can get the profile information using the user_id parameter.","type":"string","validate":"^[0-9]+$"}},"$other":{"openapi":{"hideParams":["user_id","session_id"],"showExamplesInCode":["username"]}},"method":"GET"}, cls.__get_options__(), "Public.check")(username=username, user_id=user_id, country=country, session_id=session_id, **otherParams)
	
		@classmethod
		def posts(cls, secUid: str = None, count: int = Default(30), cursor: str = None, user_id: str = None, country: str = None, session_id: int = None, **otherParams) -> APIResponse:
			'''
				Get a user's feed posts 
			'''
			count = None if count is cls.posts.__defaults__[1] else count
			return wrap({"help":"Get a user's feed posts","path":"/public/posts","comment":"<a target=\"_blank\" href='https://helpdesk.tikapi.io/portal/en/kb/articles/how-to-download-tiktok-videos'>\nLearn more about downloading videos</a>\n\n","params":{"secUid":{"validate":"^(.*?){30,}$","help":"The TikTok user secUid. You can get this from the <a href='#tag/Public/operation/public.check'>Get profile information</a> endpoint using the username.","type":"string","example":"MS4wLjABAAAAsHntXC3s0AvxcecggxsoVa4eAiT8OVafVZ4OQXxy-9htpnUi0sOYSr0kGGD1Loud","required":True},"count":{"example":30,"default":30,"max":30,"type":"number","help":"Maximum amount of items for one request","validate":"^[0-9]{1,2}$"},"cursor":{"help":"The starting point of the items list. Returned in every response, should be included in the next request for iteration.<br><br> *(A simple iteration method is already implemented in the Javascript & Python libraries as seen in the request samples)*","type":"string","validate":"^[0-9]+$"},"user_id":{"help":"The TikTok user ID","type":"string","validate":"^[0-9]+$"}},"$other":{"openapi":{"hideParams":["session_id","user_id"]}},"method":"GET"}, cls.__get_options__(), "Public.posts")(secUid=secUid, count=count, cursor=cursor, user_id=user_id, country=country, session_id=session_id, **otherParams)
	
		@classmethod
		def likes(cls, secUid: str = None, count: int = Default(30), cursor: str = None, country: str = None, session_id: int = None, **otherParams) -> APIResponse:
			'''
				Get a user's liked posts 
			'''
			count = None if count is cls.likes.__defaults__[1] else count
			return wrap({"help":"Get a user's liked posts","path":"/public/likes","comment":"<a target=\"_blank\" href='https://helpdesk.tikapi.io/portal/en/kb/articles/how-to-download-tiktok-videos'>\nLearn more about downloading videos</a>\n\n","params":{"secUid":{"validate":"^(.*?){30,}$","help":"The TikTok user secUid. You can get this from the <a href='#tag/Public/operation/public.check'>Get profile information</a> endpoint using the username.","type":"string","example":"MS4wLjABAAAAsHntXC3s0AvxcecggxsoVa4eAiT8OVafVZ4OQXxy-9htpnUi0sOYSr0kGGD1Loud","required":True},"count":{"example":30,"default":30,"max":30,"type":"number","help":"Maximum amount of items for one request","validate":"^[0-9]{1,2}$"},"cursor":{"help":"The starting point of the items list. Returned in every response, should be included in the next request for iteration.<br><br> *(A simple iteration method is already implemented in the Javascript & Python libraries as seen in the request samples)*","type":"string","validate":"^[0-9]+$"}},"$other":{"openapi":{"hideParams":["session_id"]}},"method":"GET"}, cls.__get_options__(), "Public.likes")(secUid=secUid, count=count, cursor=cursor, country=country, session_id=session_id, **otherParams)
	
		@classmethod
		def followersList(cls, secUid: str = None, count: int = Default(30), nextCursor: str = None, country: str = None, session_id: int = None, **otherParams) -> APIResponse:
			'''
				Get a user's followers list 
			'''
			count = None if count is cls.followersList.__defaults__[1] else count
			return wrap({"help":"Get a user's followers list","comment":"Get followers list of any public profile.","path":"/public/followers","params":{"secUid":{"validate":"^(.*?){30,}$","help":"The TikTok user secUid. You can get this from the <a href='#tag/Public/operation/public.check'>Get profile information</a> endpoint using the username.","type":"string","example":"MS4wLjABAAAAsHntXC3s0AvxcecggxsoVa4eAiT8OVafVZ4OQXxy-9htpnUi0sOYSr0kGGD1Loud","required":True},"count":{"example":30,"default":30,"max":30,"type":"number","help":"Maximum amount of items for one request","validate":"^[0-9]{1,2}$"},"nextCursor":{"type":"string","help":"A iteration parameter returned in each response, should be included in the next requests to get the next items."}},"$other":{"openapi":{"hideParams":["session_id"]}},"method":"GET"}, cls.__get_options__(), "Public.followersList")(secUid=secUid, count=count, nextCursor=nextCursor, country=country, session_id=session_id, **otherParams)
	
		@classmethod
		def followingList(cls, secUid: str = None, count: int = Default(30), nextCursor: str = None, country: str = None, session_id: int = None, **otherParams) -> APIResponse:
			'''
				Get a user's following list 
			'''
			count = None if count is cls.followingList.__defaults__[1] else count
			return wrap({"help":"Get a user's following list","comment":"Get following list of any public profile.","path":"/public/following","params":{"secUid":{"validate":"^(.*?){30,}$","help":"The TikTok user secUid. You can get this from the <a href='#tag/Public/operation/public.check'>Get profile information</a> endpoint using the username.","type":"string","example":"MS4wLjABAAAAsHntXC3s0AvxcecggxsoVa4eAiT8OVafVZ4OQXxy-9htpnUi0sOYSr0kGGD1Loud","required":True},"count":{"example":30,"default":30,"max":30,"type":"number","help":"Maximum amount of items for one request","validate":"^[0-9]{1,2}$"},"nextCursor":{"type":"string","help":"A iteration parameter returned in each response, should be included in the next requests to get the next items."}},"$other":{"openapi":{"hideParams":["session_id"]}},"method":"GET"}, cls.__get_options__(), "Public.followingList")(secUid=secUid, count=count, nextCursor=nextCursor, country=country, session_id=session_id, **otherParams)
	
		@classmethod
		def explore(cls, count: int = Default(30), country: str = None, session_id: int = None, **otherParams) -> APIResponse:
			'''
				Get trending posts 
			'''
			count = None if count is cls.explore.__defaults__[0] else count
			return wrap({"help":"Get trending posts","comment":"Get a list of recommended posts from the *For You* section. <br/><a target=\"_blank\" href='https://helpdesk.tikapi.io/portal/en/kb/articles/how-to-download-tiktok-videos'>\nLearn more about downloading videos</a>\n\n","path":"/public/explore","params":{"count":{"example":30,"default":30,"max":30,"type":"number","help":"Maximum amount of items for one request","validate":"^[0-9]{1,2}$"}},"$other":{"openapi":{"hideParams":["session_id"]}},"method":"GET"}, cls.__get_options__(), "Public.explore")(count=count, country=country, session_id=session_id, **otherParams)
	
		@classmethod
		def video(cls, id: str = None, country: str = None, session_id: int = None, **otherParams) -> APIResponse:
			'''
				Get video information 
			'''
			
			return wrap({"path":"/public/video","help":"Get video information","comment":"<a target=\"_blank\" href='https://helpdesk.tikapi.io/portal/en/kb/articles/how-to-download-tiktok-videos'>\nLearn more about downloading videos</a>\n\n","params":{"id":{"help":"The video ID. Can also be a short TikTok link (e.g. vm.tiktok.com/UwU)","type":"string","validate":"^([0-9]+|https?://vm.tiktok.com/[a-zA-Z0-9]+/?)$","required":True,"example":"7003402629929913605"}},"$other":{"openapi":{"hideParams":["session_id"]}},"method":"GET"}, cls.__get_options__(), "Public.video")(id=id, country=country, session_id=session_id, **otherParams)
	
		@classmethod
		def videoV2(cls, id: str = None, country: str = None, session_id: int = None, **otherParams) -> APIResponse:
			'''
				Get video information (alternative endpoint) 
			'''
			
			return wrap({"path":"/public/video/v2","help":"Get video information (alternative endpoint)","comment":"<a target=\"_blank\" href='https://helpdesk.tikapi.io/portal/en/kb/articles/how-to-download-tiktok-videos'>\nLearn more about downloading videos</a>\n\n","params":{"id":{"help":"The video ID. Can also be a short TikTok link (e.g. vm.tiktok.com/UwU)","type":"string","validate":"^([0-9]+|https?://vm.tiktok.com/[a-zA-Z0-9]+/?)$","required":True,"example":"7109178205151464746"}},"$other":{"openapi":{"hide":True,"hideParams":["session_id"]}},"method":"GET"}, cls.__get_options__(), "Public.videoV2")(id=id, country=country, session_id=session_id, **otherParams)
	
		@classmethod
		def videoV3(cls, id: str = None, username: str = None, country: str = None, session_id: int = None, **otherParams) -> APIResponse:
			'''
				Get video information (alternative endpoint) 
			'''
			
			return wrap({"path":"/public/video/v3","help":"Get video information (alternative endpoint)","comment":"<a target=\"_blank\" href='https://helpdesk.tikapi.io/portal/en/kb/articles/how-to-download-tiktok-videos'>\nLearn more about downloading videos</a>\n\n","params":{"id":{"help":"The video ID. Can also be a short TikTok link (e.g. vm.tiktok.com/UwU)","type":"string","validate":"^([0-9]+|https?://vm.tiktok.com/[a-zA-Z0-9]+/?)$","required":True,"example":"7109178205151464746"},"username":{"help":"The username of the video author.","validate":"^([a-zA-Z0-9_.]+|https?://vm.tiktok.com/[a-zA-Z0-9]+/?)$","type":"string","required":True}},"$other":{"openapi":{"hide":True,"hideParams":["session_id"]}},"method":"GET"}, cls.__get_options__(), "Public.videoV3")(id=id, username=username, country=country, session_id=session_id, **otherParams)
	
		@classmethod
		def relatedPosts(cls, video_id: str = None, country: str = None, session_id: int = None, **otherParams) -> APIResponse:
			'''
				Get related posts 
			'''
			
			return wrap({"path":"/public/related_posts","help":"Get related posts","comment":"<a target=\"_blank\" href='https://helpdesk.tikapi.io/portal/en/kb/articles/how-to-download-tiktok-videos'>\nLearn more about downloading videos</a>\n\n","params":{"video_id":{"help":"The video ID from which to get related posts. Can also be a short TikTok link (e.g. vm.tiktok.com/UwU)","type":"string","validate":"^([0-9]+|https?://vm.tiktok.com/[a-zA-Z0-9]+/?)$","required":True,"example":"7109178205151464746"}},"$other":{"openapi":{"hideParams":["session_id"],"fields":{"x-new":True}}},"method":"GET"}, cls.__get_options__(), "Public.relatedPosts")(video_id=video_id, country=country, session_id=session_id, **otherParams)
	
		@classmethod
		def playlists(cls, secUid: str = None, count: int = Default(30), cursor: str = None, country: str = None, session_id: int = None, **otherParams) -> APIResponse:
			'''
				Get a user's playlists 
			'''
			count = None if count is cls.playlists.__defaults__[1] else count
			return wrap({"path":"/public/playlists","help":"Get a user's playlists","params":{"secUid":{"validate":"^(.*?){30,}$","help":"The TikTok user secUid. You can get this from the <a href='#tag/Public/operation/public.check'>Get profile information</a> endpoint using the username.","type":"string","example":"MS4wLjABAAAAsHntXC3s0AvxcecggxsoVa4eAiT8OVafVZ4OQXxy-9htpnUi0sOYSr0kGGD1Loud","required":True},"count":{"example":30,"default":30,"max":30,"type":"number","help":"Maximum amount of items for one request","validate":"^[0-9]{1,2}$"},"cursor":{"help":"The starting point of the items list. Returned in every response, should be included in the next request for iteration.<br><br> *(A simple iteration method is already implemented in the Javascript & Python libraries as seen in the request samples)*","type":"string","validate":"^[0-9]+$"}},"$other":{"openapi":{"hideParams":["session_id"],"fields":{"x-new":True}}},"method":"GET"}, cls.__get_options__(), "Public.playlists")(secUid=secUid, count=count, cursor=cursor, country=country, session_id=session_id, **otherParams)
	
		@classmethod
		def playlistItems(cls, playlist_id = None, count: int = Default(30), cursor: str = None, country: str = None, session_id: int = None, **otherParams) -> APIResponse:
			'''
				Get a playlist items 
			'''
			count = None if count is cls.playlistItems.__defaults__[1] else count
			return wrap({"path":"/public/playlist/items","help":"Get a playlist items","params":{"playlist_id":{"validate":"^[0-9]+$","required":True,"example":"6948562344666532614","help":"The playlist ID."},"count":{"example":30,"default":30,"max":30,"type":"number","help":"Maximum amount of items for one request","validate":"^[0-9]{1,2}$"},"cursor":{"help":"The starting point of the items list. Returned in every response, should be included in the next request for iteration.<br><br> *(A simple iteration method is already implemented in the Javascript & Python libraries as seen in the request samples)*","type":"string","validate":"^[0-9]+$"}},"$other":{"openapi":{"hideParams":["session_id"],"fields":{"x-new":True}}},"method":"GET"}, cls.__get_options__(), "Public.playlistItems")(playlist_id=playlist_id, count=count, cursor=cursor, country=country, session_id=session_id, **otherParams)
	
		@classmethod
		def exploreCategory(cls, category_id = None, count: int = Default(30), country: str = None, session_id: int = None, **otherParams) -> APIResponse:
			'''
				Get explore posts by category 
			'''
			count = None if count is cls.exploreCategory.__defaults__[1] else count
			return wrap({"path":"/public/explore/category","help":"Get explore posts by category","comment":"The following categories are supported:<br/><br/>\n\t\t\t\"Comedy & Drama\": 1,<br/>\n\t\t\t\"Dance & Music\": 2,<br/>\n\t\t\t\"Relationships\": 3,<br/>\n\t\t\t\"Nature & Pets\": 4,<br/>\n\t\t\t\"Lifestyle\": 5,<br/>\n\t\t\t\"Society\": 6,<br/>\n\t\t\t\"Fashion\": 7,<br/>\n\t\t\t\"Entertainment\": 8,<br/>\n\t\t\t\"Informative\": 10,<br/>\n\t\t\t\"Sports & Outdoors\": 11,<br/>\n\t\t\t\"Auto & Vehicle\": 12,","params":{"category_id":{"validate":"^[0-9]+$","required":True,"example":"1","help":"The category ID."},"count":{"example":30,"default":30,"max":30,"type":"number","help":"Maximum amount of items for one request","validate":"^[0-9]{1,2}$"}},"$other":{"openapi":{"hide":True,"fields":{"x-new":True,"x-beta":True}}},"method":"GET"}, cls.__get_options__(), "Public.exploreCategory")(category_id=category_id, count=count, country=country, session_id=session_id, **otherParams)
	
		@classmethod
		def hashtag(cls, id: str = None, name: str = None, count: int = Default(30), cursor: str = None, country: str = None, session_id: int = None, **otherParams) -> APIResponse:
			'''
				Get hashtag posts 
			'''
			count = None if count is cls.hashtag.__defaults__[2] else count
			return wrap({"help":"Get hashtag posts","comment":"Your first request should be using the hashtag `name` parameter, then the following requests should be using the `id` parameter which you have stored from the first request (returned in response `challengeInfo > challenge > id`). <br/><a target=\"_blank\" href='https://helpdesk.tikapi.io/portal/en/kb/articles/how-to-download-tiktok-videos'>\nLearn more about downloading videos</a>\n\n","path":"/public/hashtag","params":{"id":{"validate":"^([0-9]+|https?://vm.tiktok.com/[a-zA-Z0-9]+/?)$","type":"string","help":"The hashtag ID. Can also be a short TikTok link (e.g. vm.tiktok.com/UwU)","example":"4655293"},"name":{"type":"string","help":"The hashtag name"},"count":{"example":30,"default":30,"max":30,"type":"number","help":"Maximum amount of items for one request","validate":"^[0-9]{1,2}$"},"cursor":{"help":"The starting point of the items list. Returned in every response, should be included in the next request for iteration.<br><br> *(A simple iteration method is already implemented in the Javascript & Python libraries as seen in the request samples)*","type":"string","validate":"^[0-9]+$"}},"$other":{"openapi":{"hideParams":["session_id"]}},"method":"GET"}, cls.__get_options__(), "Public.hashtag")(id=id, name=name, count=count, cursor=cursor, country=country, session_id=session_id, **otherParams)
	
		@classmethod
		def commentsList(cls, media_id: str = None, count: int = Default(30), cursor: int = None, country: str = None, session_id: int = None, **otherParams) -> APIResponse:
			'''
				Get a video comments list 
			'''
			count = None if count is cls.commentsList.__defaults__[1] else count
			return wrap({"help":"Get a video comments list","path":"/public/comment/list","params":{"media_id":{"help":"The video ID. Can also be a short TikTok link (e.g. vm.tiktok.com/UwU)","type":"string","validate":"^([0-9]+|https?://vm.tiktok.com/[a-zA-Z0-9]+/?)$","required":True,"example":"7109178205151464746"},"count":{"example":30,"default":30,"max":30,"type":"number","help":"Maximum amount of items for one request","validate":"^[0-9]{1,2}$"},"cursor":{"help":"The starting point of the items list. Returned in every response, should be included in the next request for iteration.<br><br> *(A simple iteration method is already implemented in the Javascript & Python libraries as seen in the request samples)*","type":"number","validate":"^[0-9]+$"}},"$other":{"openapi":{}},"method":"GET"}, cls.__get_options__(), "Public.commentsList")(media_id=media_id, count=count, cursor=cursor, country=country, session_id=session_id, **otherParams)
	
		@classmethod
		def commentRepliesList(cls, media_id: str = None, comment_id: str = None, count: int = Default(30), cursor: int = None, country: str = None, session_id: int = None, **otherParams) -> APIResponse:
			'''
				Get a comment replies list 
			'''
			count = None if count is cls.commentRepliesList.__defaults__[2] else count
			return wrap({"help":"Get a comment replies list","path":"/public/comment/reply/list","params":{"media_id":{"help":"The video ID. Can also be a short TikTok link (e.g. vm.tiktok.com/UwU)","type":"string","validate":"^([0-9]+|https?://vm.tiktok.com/[a-zA-Z0-9]+/?)$","required":True,"example":"7109178205151464746"},"comment_id":{"validate":"^[0-9]+$","help":"The comment ID","type":"string","required":True,"example":"7109185042560680750"},"count":{"example":30,"default":30,"max":30,"type":"number","help":"Maximum amount of items for one request","validate":"^[0-9]{1,2}$"},"cursor":{"help":"The starting point of the items list. Returned in every response, should be included in the next request for iteration.<br><br> *(A simple iteration method is already implemented in the Javascript & Python libraries as seen in the request samples)*","type":"number","validate":"^[0-9]+$"}},"$other":{"openapi":{}},"method":"GET"}, cls.__get_options__(), "Public.commentRepliesList")(media_id=media_id, comment_id=comment_id, count=count, cursor=cursor, country=country, session_id=session_id, **otherParams)
	
		@classmethod
		def music(cls, id: str = None, count: int = Default(30), cursor: str = None, country: str = None, session_id: int = None, **otherParams) -> APIResponse:
			'''
				Get music posts 
			'''
			count = None if count is cls.music.__defaults__[1] else count
			return wrap({"help":"Get music posts","comment":"Get a list of posts that are using this music. <br/><a target=\"_blank\" href='https://helpdesk.tikapi.io/portal/en/kb/articles/how-to-download-tiktok-videos'>\nLearn more about downloading videos</a>\n\n","path":"/public/music","params":{"id":{"validate":"^([0-9]+|https?://vm.tiktok.com/[a-zA-Z0-9]+/?)$","type":"string","help":"The music ID. Can also be a short TikTok link (e.g. vm.tiktok.com/UwU)","required":True,"example":"28459463"},"count":{"example":30,"default":30,"max":30,"type":"number","help":"Maximum amount of items for one request","validate":"^[0-9]{1,2}$"},"cursor":{"help":"The starting point of the items list. Returned in every response, should be included in the next request for iteration.<br><br> *(A simple iteration method is already implemented in the Javascript & Python libraries as seen in the request samples)*","type":"string","validate":"^[0-9]+$"}},"$other":{"openapi":{"hideParams":["session_id"]}},"method":"GET"}, cls.__get_options__(), "Public.music")(id=id, count=count, cursor=cursor, country=country, session_id=session_id, **otherParams)
	
		@classmethod
		def musicInfo(cls, id: str = None, country: str = None, session_id: int = None, **otherParams) -> APIResponse:
			'''
				Get music information 
			'''
			
			return wrap({"help":"Get music information","path":"/public/music/info","params":{"id":{"validate":"^([0-9]+|https?://vm.tiktok.com/[a-zA-Z0-9]+/?)$","type":"string","help":"The music ID. Can also be a short TikTok link (e.g. vm.tiktok.com/UwU)","required":True,"example":"28459463"}},"$other":{"openapi":{"hideParams":["session_id"]}},"method":"GET"}, cls.__get_options__(), "Public.musicInfo")(id=id, country=country, session_id=session_id, **otherParams)
	
		@classmethod
		def discover(cls, category: str = None, count: int = Default(30), offset: int = None, country: str = None, session_id: int = None, **otherParams) -> APIResponse:
			'''
				Discover users, music, hashtags 
			'''
			count = None if count is cls.discover.__defaults__[1] else count
			return wrap({"help":"Discover users, music, hashtags","comment":"Get popular users, music or hashtag. You can also include *Account Key* to show personalized results for the user.","path":"/public/discover/{category}","params":{"category":{"help":"The discover category","example":"users","in":["users","music","hashtag"],"location":"path","type":"string","required":True},"count":{"example":30,"default":30,"max":30,"type":"number","help":"Maximum amount of items for one request","validate":"^[0-9]{1,2}$"},"offset":{"help":"The starting offset of items list. Returned in every response, should be included in the next request for iteration.<br><br> *(A simple iteration method is already implemented in the Javascript & Python libraries as seen in the request samples)*","type":"number","validate":"^[0-9]+$"}},"$other":{"openapi":{"hideParams":["session_id"]}},"method":"GET"}, cls.__get_options__(), "Public.discover")(category=category, count=count, offset=offset, country=country, session_id=session_id, **otherParams)
	
		@classmethod
		def discoverKeyword(cls, keyword: str = None, country: str = None, session_id: int = None, **otherParams) -> APIResponse:
			'''
				Discover by keyword 
			'''
			
			return wrap({"help":"Discover by keyword","comment":"Get popular posts, users, music or hashtags from a keyword. <br><br>Limited to only a few items. If you want more, try using the <a href='#tag/Public/operation/public.search'>Search</a> endpoint instead.","path":"/public/discover/keyword","params":{"keyword":{"required":True,"example":"lilyachty","type":"string"}},"$other":{"openapi":{"hideParams":["session_id"]}},"method":"GET"}, cls.__get_options__(), "Public.discoverKeyword")(keyword=keyword, country=country, session_id=session_id, **otherParams)
	
		@classmethod
		def search(cls, category: str = None, query: str = None, session_id: int = None, nextCursor: str = None, country: str = None, **otherParams) -> APIResponse:
			'''
				Search 
			'''
			
			return wrap({"help":"Search","comment":"Search anything, users, videos, or get keyword autocomplete suggestions. <br/><a target=\"_blank\" href='https://helpdesk.tikapi.io/portal/en/kb/articles/how-to-download-tiktok-videos'>\nLearn more about downloading videos</a>\n\n","path":"/public/search/{category}","params":{"category":{"help":"The search category","in":["general","users","videos","autocomplete"],"required":True,"type":"string","example":"general","location":"path"},"query":{"type":"string","example":"lilyachty","required":True,"help":"The search keyword"},"nextCursor":{"type":"string","help":"A iteration parameter returned in each response, should be included in the next requests to get the next items."},"session_id":{"type":"number","max":100,"example":0,"help":"The cookies and IP are preserved through different requests for a longer amount of time. You should use this if you want to keep the search suggestions the same."}},"$other":{"openapi":{"hideParams":["session_id"]}},"method":"GET"}, cls.__get_options__(), "Public.search")(category=category, query=query, session_id=session_id, nextCursor=nextCursor, country=country, **otherParams)
	
	Rests.Public = Public
	class UserPostsComments(Rests.BaseClass):
		'''
			Comments Endpoints Category 
		'''

		__options__ = {"headers":{},"params":{"accountKey":{"name":"X-ACCOUNT-KEY","required":True,"help":"The Account Key is required","location":"headers","validate":"^[a-zA-Z0-9]{10,}$","example":"DemoAccountKeyTokenSeHYGXDfd4SFD320Sc39Asd0Sc39A","$initsOnly":True}},"values":{},"$other":{"openapi":{"fields":{"parameters":[],"responses":{},"tags":["Posts"],"security":[{"apiKey":[],"accountKey":["media_actions"]}]}}}}

		def __new__(self, **values) -> 'UserPostsComments':
			'''
				Initialize new 'UserPostsComments' instance with default values & options
			'''
			return super().__new__(self, **values)

		@classmethod
		def set(self, **values) -> 'UserPostsComments':
			'''
				Method is only available for the root category.
				Set default values & options for 'UserPostsComments'
			'''
			return super().set(**values)
	
		@classmethod
		def list(cls, media_id: str = None, count: int = Default(30), cursor: int = None, **otherParams) -> APIResponse:
			'''
				Get a video comments list 
			'''
			count = None if count is cls.list.__defaults__[1] else count
			return wrap({"help":"Get a video comments list","path":"/user/comment/list","params":{"media_id":{"help":"The video ID. Can also be a short TikTok link (e.g. vm.tiktok.com/UwU)","type":"string","validate":"^([0-9]+|https?://vm.tiktok.com/[a-zA-Z0-9]+/?)$","required":True,"example":"7109178205151464746"},"count":{"example":30,"default":30,"max":30,"type":"number","help":"Maximum amount of items for one request","validate":"^[0-9]{1,2}$"},"cursor":{"help":"The starting point of the items list. Returned in every response, should be included in the next request for iteration.<br><br> *(A simple iteration method is already implemented in the Javascript & Python libraries as seen in the request samples)*","type":"number","validate":"^[0-9]+$"}},"$other":{"openapi":{}},"method":"GET"}, cls.__get_options__(), "UserPostsComments.list")(media_id=media_id, count=count, cursor=cursor, **otherParams)
	
		@classmethod
		def replies(cls, media_id: str = None, comment_id: str = None, count: int = Default(30), cursor: int = None, **otherParams) -> APIResponse:
			'''
				Get a comment reply list 
			'''
			count = None if count is cls.replies.__defaults__[2] else count
			return wrap({"help":"Get a comment reply list","path":"/user/comment/reply/list","params":{"media_id":{"help":"The video ID. Can also be a short TikTok link (e.g. vm.tiktok.com/UwU)","type":"string","validate":"^([0-9]+|https?://vm.tiktok.com/[a-zA-Z0-9]+/?)$","required":True,"example":"7109178205151464746"},"comment_id":{"validate":"^[0-9]+$","help":"The comment ID","type":"string","required":True,"example":"7109185042560680750"},"count":{"example":30,"default":30,"max":30,"type":"number","help":"Maximum amount of items for one request","validate":"^[0-9]{1,2}$"},"cursor":{"help":"The starting point of the items list. Returned in every response, should be included in the next request for iteration.<br><br> *(A simple iteration method is already implemented in the Javascript & Python libraries as seen in the request samples)*","type":"number","validate":"^[0-9]+$"}},"$other":{"openapi":{}},"method":"GET"}, cls.__get_options__(), "UserPostsComments.replies")(media_id=media_id, comment_id=comment_id, count=count, cursor=cursor, **otherParams)
	
		@classmethod
		def post(cls, media_id: str = None, text: str = None, reply_comment_id: str = None, has_tags: bool = None, **otherParams) -> APIResponse:
			'''
				Post a new comment 
			'''
			
			return wrap({"path":"/user/comment","method":"POST","enctype":"json","help":"Post a new comment","comment":"*This endpoint is only available to trusted customers. \n<a target=\"_blank\" href='https://helpdesk.tikapi.io/portal/en/kb/articles/how-can-i-get-access-to-special-endpoints'> Learn more about special endpoints</a>*\n\nMake a comment or reply to a comment.","params":{"media_id":{"help":"The video ID. Can also be a short TikTok link (e.g. vm.tiktok.com/UwU)","type":"string","validate":"^([0-9]+|https?://vm.tiktok.com/[a-zA-Z0-9]+/?)$","required":True,"example":"7109178205151464746"},"text":{"required":True,"type":"string","help":"The comment text","example":"Italian food is the best"},"reply_comment_id":{"validate":"^[0-9]+$","type":"string","help":"You can reply to a comment by including a comment ID"},"has_tags":{"type":"boolean","default":False,"help":"You should set this to True if you are mentioning someone."}}}, cls.__get_options__(), "UserPostsComments.post")(media_id=media_id, text=text, reply_comment_id=reply_comment_id, has_tags=has_tags, **otherParams)
	
		@classmethod
		def like(cls, media_id: str = None, comment_id: str = None, **otherParams) -> APIResponse:
			'''
				Like a comment 
			'''
			
			return wrap({"help":"Like a comment","path":"/user/comment/like","method":"POST","enctype":"json","params":{"media_id":{"help":"The video ID. Can also be a short TikTok link (e.g. vm.tiktok.com/UwU)","type":"string","validate":"^([0-9]+|https?://vm.tiktok.com/[a-zA-Z0-9]+/?)$","required":True,"example":"7109178205151464746"},"comment_id":{"validate":"^[0-9]+$","help":"The comment ID","type":"string","required":True,"example":"7109185042560680750"}}}, cls.__get_options__(), "UserPostsComments.like")(media_id=media_id, comment_id=comment_id, **otherParams)
	
		@classmethod
		def unlike(cls, media_id: str = None, comment_id: str = None, **otherParams) -> APIResponse:
			'''
				Unlike a comment 
			'''
			
			return wrap({"help":"Unlike a comment","path":"/user/comment/unlike","method":"POST","enctype":"json","params":{"media_id":{"help":"The video ID. Can also be a short TikTok link (e.g. vm.tiktok.com/UwU)","type":"string","validate":"^([0-9]+|https?://vm.tiktok.com/[a-zA-Z0-9]+/?)$","required":True,"example":"7109178205151464746"},"comment_id":{"validate":"^[0-9]+$","help":"The comment ID","type":"string","required":True,"example":"7109185042560680750"}}}, cls.__get_options__(), "UserPostsComments.unlike")(media_id=media_id, comment_id=comment_id, **otherParams)
	
		@classmethod
		def delete(cls, comment_id: str = None, **otherParams) -> APIResponse:
			'''
				Delete a comment 
			'''
			
			return wrap({"path":"/user/comment/delete","help":"Delete a comment","comment":"*This endpoint is only available to trusted customers. \n<a target=\"_blank\" href='https://helpdesk.tikapi.io/portal/en/kb/articles/how-can-i-get-access-to-special-endpoints'> Learn more about special endpoints</a>*\n\n","method":"POST","params":{"comment_id":{"validate":"^[0-9]+$","help":"The comment ID","type":"string","required":True,"example":"7109185042560680750"}}}, cls.__get_options__(), "UserPostsComments.delete")(comment_id=comment_id, **otherParams)
	
	Rests.UserPostsComments = UserPostsComments
	class UserPosts(Rests.BaseClass):
		'''
			Posts Endpoints Category 
		'''

		__options__ = {"headers":{},"params":{"accountKey":{"name":"X-ACCOUNT-KEY","required":True,"help":"The Account Key is required","location":"headers","validate":"^[a-zA-Z0-9]{10,}$","example":"DemoAccountKeyTokenSeHYGXDfd4SFD320Sc39Asd0Sc39A","$initsOnly":True}},"values":{},"$other":{"openapi":{"fields":{"parameters":[],"responses":{},"tags":["Posts"]}}}}

		def __new__(self, **values) -> 'UserPosts':
			'''
				Initialize new 'UserPosts' instance with default values & options
			'''
			return super().__new__(self, **values)

		@classmethod
		def set(self, **values) -> 'UserPosts':
			'''
				Method is only available for the root category.
				Set default values & options for 'UserPosts'
			'''
			return super().set(**values)
	
		@classmethod
		def feed(cls, count: int = Default(30), cursor: str = None, secUid: str = None, user_id: str = None, **otherParams) -> APIResponse:
			'''
				Get feed posts 
			'''
			count = None if count is cls.feed.__defaults__[0] else count
			return wrap({"help":"Get feed posts","comment":"Get current user feed posts, or someone elses by providing the `secUid` parameter.","path":"/user/feed","params":{"count":{"example":30,"default":30,"max":30,"type":"number","help":"Maximum amount of items for one request","validate":"^[0-9]{1,2}$"},"cursor":{"help":"The starting point of the items list. Returned in every response, should be included in the next request for iteration.<br><br> *(A simple iteration method is already implemented in the Javascript & Python libraries as seen in the request samples)*","type":"string","validate":"^[0-9]+$"},"secUid":{"validate":"^(.*?){30,}$","help":"The TikTok user secUid. You can get this from the <a href='#tag/Public/operation/public.check'>Get profile information</a> endpoint using the username.","type":"string","example":"MS4wLjABAAAAsHntXC3s0AvxcecggxsoVa4eAiT8OVafVZ4OQXxy-9htpnUi0sOYSr0kGGD1Loud"},"user_id":{"help":"The TikTok user ID","type":"string","validate":"^[0-9]+$"}},"$other":{"openapi":{"fields":{"security":[{"apiKey":[],"accountKey":["explore"]}]},"hideParams":["user_id"]}},"method":"GET"}, cls.__get_options__(), "UserPosts.feed")(count=count, cursor=cursor, secUid=secUid, user_id=user_id, **otherParams)
	
		@classmethod
		def likes(cls, count: int = Default(30), secUid: str = None, cursor: str = None, **otherParams) -> APIResponse:
			'''
				Get liked posts 
			'''
			count = None if count is cls.likes.__defaults__[0] else count
			return wrap({"help":"Get liked posts","comment":"Get current user liked posts, or someone elses by providing the `secUid` parameter.","path":"/user/likes","params":{"count":{"example":30,"default":30,"max":30,"type":"number","help":"Maximum amount of items for one request","validate":"^[0-9]{1,2}$"},"secUid":{"validate":"^(.*?){30,}$","help":"The TikTok user secUid. You can get this from the <a href='#tag/Public/operation/public.check'>Get profile information</a> endpoint using the username.","type":"string","example":"MS4wLjABAAAAsHntXC3s0AvxcecggxsoVa4eAiT8OVafVZ4OQXxy-9htpnUi0sOYSr0kGGD1Loud"},"cursor":{"help":"The starting point of the items list. Returned in every response, should be included in the next request for iteration.<br><br> *(A simple iteration method is already implemented in the Javascript & Python libraries as seen in the request samples)*","type":"string","validate":"^[0-9]+$"}},"$other":{"openapi":{"fields":{"security":[{"apiKey":[],"accountKey":["explore"]}]}}},"method":"GET"}, cls.__get_options__(), "UserPosts.likes")(count=count, secUid=secUid, cursor=cursor, **otherParams)
	
		@classmethod
		def followingPosts(cls, count: int = Default(30), cursor: str = None, **otherParams) -> APIResponse:
			'''
				Get following posts 
			'''
			count = None if count is cls.followingPosts.__defaults__[0] else count
			return wrap({"path":"/user/following_posts","help":"Get following posts","comment":"<a target=\"_blank\" href='https://helpdesk.tikapi.io/portal/en/kb/articles/how-to-download-tiktok-videos'>\nLearn more about downloading videos</a>\n\n","params":{"count":{"example":30,"default":30,"max":30,"type":"number","help":"Maximum amount of items for one request","validate":"^[0-9]{1,2}$"},"cursor":{"help":"The starting point of the items list. Returned in every response, should be included in the next request for iteration.<br><br> *(A simple iteration method is already implemented in the Javascript & Python libraries as seen in the request samples)*","type":"string","validate":"^[0-9]+$"}},"$other":{"openapi":{"fields":{"x-new":True,"security":[{"apiKey":[],"accountKey":["explore"]}]}}},"method":"GET"}, cls.__get_options__(), "UserPosts.followingPosts")(count=count, cursor=cursor, **otherParams)
	
		@classmethod
		def relatedPosts(cls, video_id: str = None, **otherParams) -> APIResponse:
			'''
				Get related posts 
			'''
			
			return wrap({"path":"/user/related_posts","help":"Get related posts","comment":"<a target=\"_blank\" href='https://helpdesk.tikapi.io/portal/en/kb/articles/how-to-download-tiktok-videos'>\nLearn more about downloading videos</a>\n\n","params":{"video_id":{"help":"The video ID from which to get related posts. Can also be a short TikTok link (e.g. vm.tiktok.com/UwU)","type":"string","validate":"^([0-9]+|https?://vm.tiktok.com/[a-zA-Z0-9]+/?)$","required":True,"example":"7109178205151464746"}},"$other":{"openapi":{"fields":{"x-new":True,"security":[{"apiKey":[],"accountKey":["explore"]}]}}},"method":"GET"}, cls.__get_options__(), "UserPosts.relatedPosts")(video_id=video_id, **otherParams)
	
		@classmethod
		def savedPosts(cls, count: int = Default(30), cursor: str = None, **otherParams) -> APIResponse:
			'''
				Get saved posts 
			'''
			count = None if count is cls.savedPosts.__defaults__[0] else count
			return wrap({"path":"/user/saved","help":"Get saved posts","comment":"<a target=\"_blank\" href='https://helpdesk.tikapi.io/portal/en/kb/articles/how-to-download-tiktok-videos'>\nLearn more about downloading videos</a>\n\n","params":{"count":{"example":30,"default":30,"max":30,"type":"number","help":"Maximum amount of items for one request","validate":"^[0-9]{1,2}$"},"cursor":{"help":"The starting point of the items list. Returned in every response, should be included in the next request for iteration.<br><br> *(A simple iteration method is already implemented in the Javascript & Python libraries as seen in the request samples)*","type":"string","validate":"^[0-9]+$"}},"$other":{"openapi":{"fields":{"x-new":True,"security":[{"apiKey":[],"accountKey":["view_collections"]}]}}},"method":"GET"}, cls.__get_options__(), "UserPosts.savedPosts")(count=count, cursor=cursor, **otherParams)
	
		@classmethod
		def playlists(cls, secUid: str = None, count: int = Default(30), cursor: str = None, **otherParams) -> APIResponse:
			'''
				Get user playlists 
			'''
			count = None if count is cls.playlists.__defaults__[1] else count
			return wrap({"path":"/user/playlists","help":"Get user playlists","params":{"secUid":{"validate":"^(.*?){30,}$","help":"The TikTok user secUid. You can get this from the <a href='#tag/Public/operation/public.check'>Get profile information</a> endpoint using the username.","type":"string","example":"MS4wLjABAAAAsHntXC3s0AvxcecggxsoVa4eAiT8OVafVZ4OQXxy-9htpnUi0sOYSr0kGGD1Loud","required":False},"count":{"example":30,"default":30,"max":30,"type":"number","help":"Maximum amount of items for one request","validate":"^[0-9]{1,2}$"},"cursor":{"help":"The starting point of the items list. Returned in every response, should be included in the next request for iteration.<br><br> *(A simple iteration method is already implemented in the Javascript & Python libraries as seen in the request samples)*","type":"string","validate":"^[0-9]+$"}},"$other":{"openapi":{"fields":{"x-new":True,"security":[{"apiKey":[],"accountKey":["view_collections"]}]}}},"method":"GET"}, cls.__get_options__(), "UserPosts.playlists")(secUid=secUid, count=count, cursor=cursor, **otherParams)
	
		@classmethod
		def playlistItems(cls, playlist_id = None, count: int = Default(30), cursor: str = None, **otherParams) -> APIResponse:
			'''
				Get a playlist items 
			'''
			count = None if count is cls.playlistItems.__defaults__[1] else count
			return wrap({"path":"/user/playlist/items","help":"Get a playlist items","params":{"playlist_id":{"validate":"^[0-9]+$","required":True,"example":"6948562344666532614","help":"The playlist ID."},"count":{"example":30,"default":30,"max":30,"type":"number","help":"Maximum amount of items for one request","validate":"^[0-9]{1,2}$"},"cursor":{"help":"The starting point of the items list. Returned in every response, should be included in the next request for iteration.<br><br> *(A simple iteration method is already implemented in the Javascript & Python libraries as seen in the request samples)*","type":"string","validate":"^[0-9]+$"}},"$other":{"openapi":{"fields":{"x-new":True,"security":[{"apiKey":[],"accountKey":["view_collections"]}]}}},"method":"GET"}, cls.__get_options__(), "UserPosts.playlistItems")(playlist_id=playlist_id, count=count, cursor=cursor, **otherParams)
	
		@classmethod
		def explore(cls, count: int = Default(30), **otherParams) -> APIResponse:
			'''
				Get trending posts 
			'''
			count = None if count is cls.explore.__defaults__[0] else count
			return wrap({"help":"Get trending posts","comment":"Get current user recommended posts from the *For You* section.","path":"/user/explore","params":{"count":{"example":30,"default":30,"max":30,"type":"number","help":"Maximum amount of items for one request","validate":"^[0-9]{1,2}$"}},"$other":{"openapi":{"fields":{"security":[{"apiKey":[],"accountKey":["explore"]}]}}},"method":"GET"}, cls.__get_options__(), "UserPosts.explore")(count=count, **otherParams)
	
		@classmethod
		def search(cls, category: str = None, query: str = None, nextCursor: str = None, **otherParams) -> APIResponse:
			'''
				Search 
			'''
			
			return wrap({"help":"Search","comment":"Search anything, users, videos, or get keyword autocomplete suggestions. Using this instead of the Public Search endpoint will give you more personalized and consistent results. <br/><a target=\"_blank\" href='https://helpdesk.tikapi.io/portal/en/kb/articles/how-to-download-tiktok-videos'>\nLearn more about downloading videos</a>\n\n","path":"/user/search/{category}","params":{"category":{"help":"The search category","in":["general","users","videos","autocomplete"],"required":True,"type":"string","example":"general","location":"path"},"query":{"type":"string","example":"lilyachty","required":True,"help":"The search keyword"},"nextCursor":{"type":"string","help":"A iteration parameter returned in each response, should be included in the next requests to get the next items."}},"$other":{"openapi":{"fields":{"security":[{"apiKey":[],"accountKey":["explore"]}]}}},"method":"GET"}, cls.__get_options__(), "UserPosts.search")(category=category, query=query, nextCursor=nextCursor, **otherParams)
	
		@classmethod
		def video(cls, id: str = None, **otherParams) -> APIResponse:
			'''
				Get video information 
			'''
			
			return wrap({"help":"Get video information","comment":"<a target=\"_blank\" href='https://helpdesk.tikapi.io/portal/en/kb/articles/how-to-download-tiktok-videos'>\nLearn more about downloading videos</a>\n\n","path":"/user/video","params":{"id":{"help":"The video ID. Can also be a short TikTok link (e.g. vm.tiktok.com/UwU)","type":"string","validate":"^([0-9]+|https?://vm.tiktok.com/[a-zA-Z0-9]+/?)$","required":True,"example":"7003402629929913605"}},"$other":{"openapi":{"fields":{"security":[{"apiKey":[],"accountKey":["explore"]}]}}},"method":"GET"}, cls.__get_options__(), "UserPosts.video")(id=id, **otherParams)
	
		@classmethod
		def like(cls, media_id: str = None, **otherParams) -> APIResponse:
			'''
				Like a video 
			'''
			
			return wrap({"help":"Like a video","comment":"*This endpoint is only available to trusted customers. \n<a target=\"_blank\" href='https://helpdesk.tikapi.io/portal/en/kb/articles/how-can-i-get-access-to-special-endpoints'> Learn more about special endpoints</a>*\n\n","path":"/user/like","method":"POST","enctype":"json","params":{"media_id":{"help":"The video ID. Can also be a short TikTok link (e.g. vm.tiktok.com/UwU)","type":"string","validate":"^([0-9]+|https?://vm.tiktok.com/[a-zA-Z0-9]+/?)$","required":True,"example":"7109178205151464746"}},"$other":{"openapi":{"fields":{"security":[{"apiKey":[],"accountKey":["media_actions"]}]}}}}, cls.__get_options__(), "UserPosts.like")(media_id=media_id, **otherParams)
	
		@classmethod
		def unlike(cls, media_id: str = None, **otherParams) -> APIResponse:
			'''
				Unlike a video 
			'''
			
			return wrap({"help":"Unlike a video","comment":"*This endpoint is only available to trusted customers. \n<a target=\"_blank\" href='https://helpdesk.tikapi.io/portal/en/kb/articles/how-can-i-get-access-to-special-endpoints'> Learn more about special endpoints</a>*\n\n","path":"/user/unlike","method":"POST","enctype":"json","params":{"media_id":{"help":"The video ID. Can also be a short TikTok link (e.g. vm.tiktok.com/UwU)","type":"string","validate":"^([0-9]+|https?://vm.tiktok.com/[a-zA-Z0-9]+/?)$","required":True,"example":"7109178205151464746"}},"$other":{"openapi":{"fields":{"security":[{"apiKey":[],"accountKey":["media_actions"]}]}}}}, cls.__get_options__(), "UserPosts.unlike")(media_id=media_id, **otherParams)
	
		comments = Rests.UserPostsComments
	Rests.UserPosts = UserPosts
	class UserConversationRequests(Rests.BaseClass):
		'''
			ConversationRequests Endpoints Category 
		'''

		__options__ = {"headers":{},"params":{"accountKey":{"name":"X-ACCOUNT-KEY","required":True,"help":"The Account Key is required","location":"headers","validate":"^[a-zA-Z0-9]{10,}$","example":"DemoAccountKeyTokenSeHYGXDfd4SFD320Sc39Asd0Sc39A","$initsOnly":True}},"values":{},"$other":{"openapi":{"fields":{"parameters":[],"responses":{},"tags":["Messages"],"security":[{"apiKey":[],"accountKey":["conversation_requests"]}],"x-new":True}}}}

		def __new__(self, **values) -> 'UserConversationRequests':
			'''
				Initialize new 'UserConversationRequests' instance with default values & options
			'''
			return super().__new__(self, **values)

		@classmethod
		def set(self, **values) -> 'UserConversationRequests':
			'''
				Method is only available for the root category.
				Set default values & options for 'UserConversationRequests'
			'''
			return super().set(**values)
	
		@classmethod
		def conversations(cls, nextCursor: int = None, **otherParams) -> APIResponse:
			'''
				Get user conversation requests 
			'''
			
			return wrap({"path":"/user/conversations/requests","help":"Get user conversation requests","comment":"**Premium**<img title='Only Business and Enterprise subscriptions can access this\nendpoint' style='margin-bottom: -3px;cursor: help;'\nsrc='/assets/img/star.png' width='18px'><br/>\nGet a list of current user conversations requests including the latest message.","params":{"nextCursor":{"help":"The starting offset of items list. Returned in every response, should be included in the next request for iteration.<br><br> *(A simple iteration method is already implemented in the Javascript & Python libraries as seen in the request samples)*","type":"number","validate":"^[0-9]+$"}},"$other":{"openapi":{}},"method":"GET"}, cls.__get_options__(), "UserConversationRequests.conversations")(nextCursor=nextCursor, **otherParams)
	
		@classmethod
		def messages(cls, conversation_id = None, conversation_short_id = None, **otherParams) -> APIResponse:
			'''
				Get a conversation request messages 
			'''
			
			return wrap({"path":"/user/messages/requests","help":"Get a conversation request messages","comment":"**Premium**<img title='Only Business and Enterprise subscriptions can access this\nendpoint' style='margin-bottom: -3px;cursor: help;'\nsrc='/assets/img/star.png' width='18px'><br/>\nGet the messages of a conversation in the requests tab (generally there is a 3 message limit).","params":{"conversation_id":{"help":"The conversation ID","required":True,"example":"0:1:684574219823284956:69402435203845897564"},"conversation_short_id":{"help":"The additional conversation short ID","required":True,"example":"6940245147502654884"}},"method":"GET"}, cls.__get_options__(), "UserConversationRequests.messages")(conversation_id=conversation_id, conversation_short_id=conversation_short_id, **otherParams)
	
		@classmethod
		def markRead(cls, conversation_id = None, conversation_short_id = None, **otherParams) -> APIResponse:
			'''
				Mark a requests conversation as read 
			'''
			
			return wrap({"path":"/user/conversations/requests/mark_read","help":"Mark a requests conversation as read","comment":"**Premium**<img title='Only Business and Enterprise subscriptions can access this\nendpoint' style='margin-bottom: -3px;cursor: help;'\nsrc='/assets/img/star.png' width='18px'><br/>\n","params":{"conversation_id":{"help":"The conversation ID","required":True,"example":"0:1:684574219823284956:69402435203845897564"},"conversation_short_id":{"help":"The additional conversation short ID","required":True,"example":"6940245147502654884"}},"$other":{"openapi":{"hide":True}},"method":"GET"}, cls.__get_options__(), "UserConversationRequests.markRead")(conversation_id=conversation_id, conversation_short_id=conversation_short_id, **otherParams)
	
		@classmethod
		def delete(cls, conversation_id = None, conversation_short_id = None, **otherParams) -> APIResponse:
			'''
				Delete a conversation request 
			'''
			
			return wrap({"path":"/user/conversations/requests/delete","help":"Delete a conversation request","comment":"**Premium**<img title='Only Business and Enterprise subscriptions can access this\nendpoint' style='margin-bottom: -3px;cursor: help;'\nsrc='/assets/img/star.png' width='18px'><br/>\n","params":{"conversation_id":{"help":"The conversation ID","required":True,"example":"0:1:684574219823284956:69402435203845897564"},"conversation_short_id":{"help":"The additional conversation short ID","required":True,"example":"6940245147502654884"}},"method":"GET"}, cls.__get_options__(), "UserConversationRequests.delete")(conversation_id=conversation_id, conversation_short_id=conversation_short_id, **otherParams)
	
		@classmethod
		def accept(cls, conversation_id = None, conversation_short_id = None, user_id: str = None, **otherParams) -> APIResponse:
			'''
				Accept a conversation request 
			'''
			
			return wrap({"path":"/user/conversations/requests/accept","help":"Accept a conversation request","comment":"**Premium**<img title='Only Business and Enterprise subscriptions can access this\nendpoint' style='margin-bottom: -3px;cursor: help;'\nsrc='/assets/img/star.png' width='18px'><br/>\n","params":{"conversation_id":{"help":"The conversation ID","required":True,"example":"0:1:684574219823284956:69402435203845897564"},"conversation_short_id":{"help":"The additional conversation short ID","required":True,"example":"6940245147502654884"},"user_id":{"help":"The sender ID.","type":"string","validate":"^[0-9]+$","required":True,"example":"6569595380449902597"}},"method":"GET"}, cls.__get_options__(), "UserConversationRequests.accept")(conversation_id=conversation_id, conversation_short_id=conversation_short_id, user_id=user_id, **otherParams)
	
	Rests.UserConversationRequests = UserConversationRequests
	class UserLive(Rests.BaseClass):
		'''
			Live Endpoints Category 
		'''

		__options__ = {"headers":{},"params":{"accountKey":{"name":"X-ACCOUNT-KEY","required":True,"help":"The Account Key is required","location":"headers","validate":"^[a-zA-Z0-9]{10,}$","example":"DemoAccountKeyTokenSeHYGXDfd4SFD320Sc39Asd0Sc39A","$initsOnly":True}},"values":{},"$other":{"openapi":{"fields":{"parameters":[],"responses":{},"tags":["Live"],"security":[{"apiKey":[],"accountKey":["live"]}]}}}}

		def __new__(self, **values) -> 'UserLive':
			'''
				Initialize new 'UserLive' instance with default values & options
			'''
			return super().__new__(self, **values)

		@classmethod
		def set(self, **values) -> 'UserLive':
			'''
				Method is only available for the root category.
				Set default values & options for 'UserLive'
			'''
			return super().set(**values)
	
		@classmethod
		def permissions(cls, **otherParams) -> APIResponse:
			'''
				Check live permissions 
			'''
			
			return wrap({"help":"Check live permissions","comment":"Check current user live permissions. You can use this to check if the user has third_party streaming enabled.","path":"/user/live/info","method":"GET","params":{}}, cls.__get_options__(), "UserLive.permissions")(**otherParams)
	
		@classmethod
		def start(cls, title = None, third_party = Default(True), hashtag_id: int = None, game_tag_id: int = None, **otherParams) -> APIResponse:
			'''
				Start live video 
			'''
			third_party = None if third_party is cls.start.__defaults__[1] else third_party
			return wrap({"help":"Start live video","path":"/user/live/start","method":"POST","enctype":"json","comment":"**Premium**<img title='Only Business and Enterprise subscriptions can access this\nendpoint' style='margin-bottom: -3px;cursor: help;'\nsrc='/assets/img/star.png' width='18px'><br/>\nStart a live video, if the user has live enabled.\n\t\t\t\tThe live is closed automatically after stream ends.","params":{"title":{"required":True,"example":"Check out my live!","help":"The live room header title"},"third_party":{"default":True,"help":"TikTok has a special gateway for invite only users. Only if this is enabled you can do third party streaming."},"hashtag_id":{"help":"(Optional) The topic ID. You can find this by using the <a href='#tag/Live/operation/user.live.topics'>Get topics list</a> endpoint.","type":"number"},"game_tag_id":{"help":"(Optional) The sub-topic ID for gaming topics.","type":"number"}}}, cls.__get_options__(), "UserLive.start")(title=title, third_party=third_party, hashtag_id=hashtag_id, game_tag_id=game_tag_id, **otherParams)
	
		@classmethod
		def stop(cls, **otherParams) -> APIResponse:
			'''
				Stop live video 
			'''
			
			return wrap({"help":"Stop live video","comment":"**Premium**<img title='Only Business and Enterprise subscriptions can access this\nendpoint' style='margin-bottom: -3px;cursor: help;'\nsrc='/assets/img/star.png' width='18px'><br/>\n","path":"/user/live/stop","method":"POST","enctype":"json","params":{}}, cls.__get_options__(), "UserLive.stop")(**otherParams)
	
		@classmethod
		def info(cls, room_id: str = None, **otherParams) -> APIResponse:
			'''
				Get live information 
			'''
			
			return wrap({"help":"Get live information","comment":"Get information about a live video. <br/>You can use this for any user\n\t\t\t\tthat has an open live video. There is a `roomId` parameter included when\n\t\t\t\tfetching profile information about users.","path":"/user/live/check","params":{"room_id":{"help":"The Live room ID. You can find this using the <a href='#tag/Public/operation/public.check'>Get profile information</a> endpoint.","type":"string","example":"7112492061034646278","required":True}},"method":"GET"}, cls.__get_options__(), "UserLive.info")(room_id=room_id, **otherParams)
	
		@classmethod
		def recommend(cls, room_id: str = None, **otherParams) -> APIResponse:
			'''
				Get recommended live videos 
			'''
			
			return wrap({"help":"Get recommended live videos","path":"/user/live/recommend","comment":"Get a list of recommended live videos, related with a live video.","params":{"room_id":{"help":"The Live room ID. You can find this using the <a href='#tag/Public/operation/public.check'>Get profile information</a> endpoint.","type":"string","example":"7112492061034646278","required":True}},"method":"GET"}, cls.__get_options__(), "UserLive.recommend")(room_id=room_id, **otherParams)
	
		@classmethod
		def stats(cls, room_id: str = None, **otherParams) -> APIResponse:
			'''
				Get live statistics 
			'''
			
			return wrap({"help":"Get live statistics","comment":"Get statistics for the current user live video, after it has ended.","path":"/user/live/stats","params":{"room_id":{"help":"The Live room ID. You can find this using the <a href='#tag/Public/operation/public.check'>Get profile information</a> endpoint.","type":"string","example":"7112492061034646278","required":True}},"method":"GET"}, cls.__get_options__(), "UserLive.stats")(room_id=room_id, **otherParams)
	
		@classmethod
		def chat(cls, room_id: str = None, nextCursor: str = None, **otherParams) -> APIResponse:
			'''
				Get live chat and gifts 
			'''
			
			return wrap({"help":"Get live chat and gifts","comment":"**Premium**<img title='Only Business and Enterprise subscriptions can access this\nendpoint' style='margin-bottom: -3px;cursor: help;'\nsrc='/assets/img/star.png' width='18px'><br/>\nGet real-time live chat, gifts, and other events for any live video.","path":"/user/live/chat","params":{"room_id":{"help":"The Live room ID. You can find this using the <a href='#tag/Public/operation/public.check'>Get profile information</a> endpoint.","type":"string","example":"7112492061034646278","required":True},"nextCursor":{"type":"string","help":"Returned in each response, should be included in the next requests to get the next chat events."}},"$other":{"openapi":{"fields":{"security":[{"apiKey":[],"accountKey":["live","send_messages"]}]}}},"method":"GET"}, cls.__get_options__(), "UserLive.chat")(room_id=room_id, nextCursor=nextCursor, **otherParams)
	
		@classmethod
		def sendChat(cls, room_id: str = None, text: str = None, **otherParams) -> APIResponse:
			'''
				Send a message to a live chat 
			'''
			
			return wrap({"help":"Send a message to a live chat","comment":"**Premium**<img title='Only Business and Enterprise subscriptions can access this\nendpoint' style='margin-bottom: -3px;cursor: help;'\nsrc='/assets/img/star.png' width='18px'><br/>\n*This endpoint is only available to trusted customers. \n<a target=\"_blank\" href='https://helpdesk.tikapi.io/portal/en/kb/articles/how-can-i-get-access-to-special-endpoints'> Learn more about special endpoints</a>*\n\nSend a chat message to any live video","path":"/user/live/chat/send","method":"POST","params":{"room_id":{"help":"The Live room ID. You can find this using the <a href='#tag/Public/operation/public.check'>Get profile information</a> endpoint.","type":"string","example":"7112492061034646278","required":True},"text":{"required":True,"type":"string","help":"The chat text message","example":"A mí me gusta"}}}, cls.__get_options__(), "UserLive.sendChat")(room_id=room_id, text=text, **otherParams)
	
		@classmethod
		def topics(cls, **otherParams) -> APIResponse:
			'''
				Get live topics list 
			'''
			
			return wrap({"help":"Get live topics list","path":"/user/live/topics","method":"GET","params":{}}, cls.__get_options__(), "UserLive.topics")(**otherParams)
	
		@classmethod
		def transactionHistory(cls, page = None, count = None, **otherParams) -> APIResponse:
			'''
				Get coin transactions history 
			'''
			
			return wrap({"help":"Get coin transactions history","path":"/user/wallet/transactions","params":{"page":{"help":"The list page number","example":1},"count":{"help":"The items limit per page","example":12}},"$other":{"openapi":{"fields":{"security":[{"apiKey":[],"accountKey":["view_coins"]}]}}},"method":"GET"}, cls.__get_options__(), "UserLive.transactionHistory")(page=page, count=count, **otherParams)
	
		@classmethod
		def search(cls, query: str = None, cursor: int = None, **otherParams) -> APIResponse:
			'''
				Search live videos 
			'''
			
			return wrap({"help":"Search live videos","path":"/user/search/live","params":{"query":{"type":"string","example":"lilyachty","required":True,"help":"The search keyword"},"cursor":{"help":"The starting offset of items list. Returned in every response, should be included in the next request for iteration.<br><br> *(A simple iteration method is already implemented in the Javascript & Python libraries as seen in the request samples)*","type":"number","validate":"^[0-9]+$"}},"$other":{"openapi":{"fields":{"x-new":True}}},"method":"GET"}, cls.__get_options__(), "UserLive.search")(query=query, cursor=cursor, **otherParams)
	
		@classmethod
		def analytics(cls, days: int = Default(7), **otherParams) -> APIResponse:
			'''
				Get live analytics 
			'''
			days = None if days is cls.analytics.__defaults__[0] else days
			return wrap({"help":"Get live analytics","path":"/user/live/analytics","params":{"days":{"default":7,"help":"The days time frame for the analytics data","validate":"^[0-9]+$","type":"number"}},"$other":{"openapi":{"fields":{"x-new":True,"security":[{"apiKey":[],"accountKey":["view_analytics"]}]}}},"method":"GET"}, cls.__get_options__(), "UserLive.analytics")(days=days, **otherParams)
	
		@classmethod
		def list(cls, count: int = Default(30), offset: int = None, sort: int = None, **otherParams) -> APIResponse:
			'''
				Get live videos list 
			'''
			count = None if count is cls.list.__defaults__[0] else count
			return wrap({"help":"Get live videos list","path":"/user/live/list","params":{"count":{"example":30,"default":30,"max":30,"type":"number","help":"Maximum amount of items for one request","validate":"^[0-9]{1,2}$"},"offset":{"help":"The starting offset of items list. Returned in every response, should be included in the next request for iteration.<br><br> *(A simple iteration method is already implemented in the Javascript & Python libraries as seen in the request samples)*","type":"number","validate":"^[0-9]+$"},"sort":{"help":"Sort results by ascending (1) or descending (0). Default is descending (0).","in":[0,1],"default":0,"type":"number","example":1}},"$other":{"openapi":{"fields":{"x-new":True}}},"method":"GET"}, cls.__get_options__(), "UserLive.list")(count=count, offset=offset, sort=sort, **otherParams)
	
		@classmethod
		def details(cls, room_id: str = None, **otherParams) -> APIResponse:
			'''
				Get a live video details 
			'''
			
			return wrap({"help":"Get a live video details","path":"/user/live/detail","params":{"room_id":{"help":"The Live room ID.","type":"string","example":"7112492061034646278","required":True}},"$other":{"openapi":{"fields":{"x-new":True}}},"method":"GET"}, cls.__get_options__(), "UserLive.details")(room_id=room_id, **otherParams)
	
	Rests.UserLive = UserLive
	class User(Rests.BaseClass):
		'''
			The user endpoints require an `accountKey` 
		'''

		__options__ = {"headers":{},"params":{"accountKey":{"name":"X-ACCOUNT-KEY","required":True,"help":"The Account Key is required","location":"headers","validate":"^[a-zA-Z0-9]{10,}$","example":"DemoAccountKeyTokenSeHYGXDfd4SFD320Sc39Asd0Sc39A","$initsOnly":True}},"values":{},"$other":{"openapi":{"fields":{"parameters":[],"responses":{}}}}}

		def __new__(self, accountKey = None, **values) -> 'User':
			'''
				Initialize new 'User' instance with default values & options
			'''
			return super().__new__(self, accountKey=accountKey, **values)

		@classmethod
		def set(self, accountKey = None, **values) -> 'User':
			'''
				Method is only available for the root category.
				Set default values & options for 'User'
			'''
			return super().set(accountKey=accountKey, **values)
	
		@classmethod
		def info(cls, username: str = None, **otherParams) -> APIResponse:
			'''
				Get profile information 
			'''
			
			return wrap({"help":"Get profile information","comment":"Get current user profile information, or another user's by specifying the username.","path":"/user/info","params":{"username":{"help":"The TikTok user username","validate":"^([a-zA-Z0-9_.]+|https?://vm.tiktok.com/[a-zA-Z0-9]+/?)$","type":"string"}},"$other":{"openapi":{"fields":{"security":[{"apiKey":[],"accountKey":["view_profile"]}],"tags":["Profile"]}}},"method":"GET"}, cls.__get_options__(), "User.info")(username=username, **otherParams)
	
		@classmethod
		def edit(cls, field: str = None, value: str = None, **otherParams) -> APIResponse:
			'''
				Edit profile 
			'''
			
			return wrap({"help":"Edit profile","comment":"**Premium**<img title='Only Business and Enterprise subscriptions can access this\nendpoint' style='margin-bottom: -3px;cursor: help;'\nsrc='/assets/img/star.png' width='18px'><br/>\nUpdate the current user profile fields.","path":"/user/edit/{field}","method":"POST","params":{"field":{"required":True,"help":"The profile field.","in":["nickname","username","bio","private"],"example":"bio","location":"path","type":"string"},"value":{"required":True,"type":"string","example":"My new bio","help":"The new field value"}},"$other":{"openapi":{"fields":{"security":[{"apiKey":[],"accountKey":["edit"]}],"tags":["Profile"]}}}}, cls.__get_options__(), "User.edit")(field=field, value=value, **otherParams)
	
		@classmethod
		def notifications(cls, filter: str = Default("all"), count: int = Default(30), max_time = None, min_time = None, **otherParams) -> APIResponse:
			'''
				Get notifications 
			'''
			filter = None if filter is cls.notifications.__defaults__[0] else filter
			count = None if count is cls.notifications.__defaults__[1] else count
			return wrap({"help":"Get notifications","comment":"Get current user recent notifications.<br><br>*Note: Some notifications are limited by TikTok.*","path":"/user/notifications","params":{"filter":{"default":"all","help":"Filter notifications by type","type":"string","in":["all","likes","comments","mentions","followers"]},"count":{"example":30,"default":30,"max":30,"type":"number","help":"Maximum amount of items for one request","validate":"^[0-9]{1,2}$"},"max_time":{"name":"max_time","help":"Returned in every response, should be included in the next request for iteration.","validate":"^[0-9]+$"},"min_time":{"help":"Returned in every response, should be included in the next request for iteration.","name":"min_time","validate":"^[0-9]+$"}},"$other":{"openapi":{"fields":{"security":[{"apiKey":[],"accountKey":["view_notifications"]}],"tags":["Profile"]}}},"method":"GET"}, cls.__get_options__(), "User.notifications")(filter=filter, count=count, max_time=max_time, min_time=min_time, **otherParams)
	
		@classmethod
		def analytics(cls, type: str = None, days: int = Default(7), media_id = None, **otherParams) -> APIResponse:
			'''
				Get analytics 
			'''
			days = None if days is cls.analytics.__defaults__[1] else days
			return wrap({"help":"Get analytics","comment":"Get analytics for business or creator accounts","path":"/creator/analytics/{type}","params":{"type":{"required":True,"in":["overview","content","video","followers","live"],"type":"string","help":"The analytics type","example":"overview","location":"path"},"days":{"default":7,"help":"The days time frame for the analytics data","validate":"^[0-9]+$","type":"number"},"media_id":{"help":"Required only for **video** type analytics, otherwise don't include.","validate":"^[0-9]+$"}},"$other":{"openapi":{"fields":{"security":[{"apiKey":[],"accountKey":["view_analytics"]}],"tags":["Profile"]}}},"method":"GET"}, cls.__get_options__(), "User.analytics")(type=type, days=days, media_id=media_id, **otherParams)
	
		@classmethod
		def verify(cls, **otherParams) -> APIResponse:
			'''
				Check session 
			'''
			
			return wrap({"help":"Check session","comment":"Check if the current user's session is valid. Auto-removes the user if it's invalid. <br><br>*Note: The session is automatically checked, though you can still manually call this endpoint if you are having issues with a user.*","path":"/user/session/check","$other":{"openapi":{"fields":{"security":[{"apiKey":[],"accountKey":["view_profile"]}],"tags":["Profile"],"responses":{"428":{"$ref":"./error_responses/428.yaml"}}}}},"method":"GET","params":{}}, cls.__get_options__(), "User.verify")(**otherParams)
	
		@classmethod
		def followingV1(cls, count: int = Default(30), cursor: int = None, **otherParams) -> APIResponse:
			'''
				Get following list 
			'''
			count = None if count is cls.followingV1.__defaults__[0] else count
			return wrap({"help":"Get following list","comment":"Get current user's following list","path":"/user/following/v1","params":{"count":{"example":30,"default":30,"max":30,"type":"number","help":"Maximum amount of items for one request","validate":"^[0-9]{1,2}$"},"cursor":{"help":"The starting point of the items list. Returned in every response, should be included in the next request for iteration.<br><br> *(A simple iteration method is already implemented in the Javascript & Python libraries as seen in the request samples)*","type":"number","validate":"^[0-9]+$"}},"$other":{"openapi":{"hide":True,"fields":{"tags":["Followers"],"security":[{"apiKey":[],"accountKey":["view_followers"]}]}}},"method":"GET"}, cls.__get_options__(), "User.followingV1")(count=count, cursor=cursor, **otherParams)
	
		@classmethod
		def following(cls, secUid: str = None, count: int = Default(30), nextCursor: str = None, **otherParams) -> APIResponse:
			'''
				Get following list 
			'''
			count = None if count is cls.following.__defaults__[1] else count
			return wrap({"help":"Get following list","comment":"Get current user following list (or a friends by specifying the secUid).","path":"/user/following","params":{"secUid":{"validate":"^(.*?){30,}$","help":"The TikTok user secUid. You can get this from the <a href='#tag/Public/operation/public.check'>Get profile information</a> endpoint using the username.","type":"string","example":"MS4wLjABAAAAsHntXC3s0AvxcecggxsoVa4eAiT8OVafVZ4OQXxy-9htpnUi0sOYSr0kGGD1Loud"},"count":{"example":30,"default":30,"max":30,"type":"number","help":"Maximum amount of items for one request","validate":"^[0-9]{1,2}$"},"nextCursor":{"type":"string","help":"A iteration parameter returned in each response, should be included in the next requests to get the next items."}},"$other":{"openapi":{"fields":{"tags":["Followers"],"security":[{"apiKey":[],"accountKey":["view_followers"]}]}}},"method":"GET"}, cls.__get_options__(), "User.following")(secUid=secUid, count=count, nextCursor=nextCursor, **otherParams)
	
		@classmethod
		def followers(cls, secUid: str = None, count: int = Default(30), nextCursor: str = None, **otherParams) -> APIResponse:
			'''
				Get followers list 
			'''
			count = None if count is cls.followers.__defaults__[1] else count
			return wrap({"help":"Get followers list","comment":"Get current user followers list (or a friends by specifying the secUid).","path":"/user/followers","params":{"secUid":{"validate":"^(.*?){30,}$","help":"The TikTok user secUid. You can get this from the <a href='#tag/Public/operation/public.check'>Get profile information</a> endpoint using the username.","type":"string","example":"MS4wLjABAAAAsHntXC3s0AvxcecggxsoVa4eAiT8OVafVZ4OQXxy-9htpnUi0sOYSr0kGGD1Loud"},"count":{"example":30,"default":30,"max":30,"type":"number","help":"Maximum amount of items for one request","validate":"^[0-9]{1,2}$"},"nextCursor":{"type":"string","help":"A iteration parameter returned in each response, should be included in the next requests to get the next items."}},"$other":{"openapi":{"fields":{"tags":["Followers"],"security":[{"apiKey":[],"accountKey":["view_followers"]}]}}},"method":"GET"}, cls.__get_options__(), "User.followers")(secUid=secUid, count=count, nextCursor=nextCursor, **otherParams)
	
		@classmethod
		def follow(cls, username: str = None, secUid: str = None, user_id: str = None, **otherParams) -> APIResponse:
			'''
				Follow a user 
			'''
			
			return wrap({"help":"Follow a user","comment":"*This endpoint is only available to trusted customers. \n<a target=\"_blank\" href='https://helpdesk.tikapi.io/portal/en/kb/articles/how-can-i-get-access-to-special-endpoints'> Learn more about special endpoints</a>*\n\n<br>This endpoint is deprecated and might not work as excpeted.","path":"/user/follow","method":"POST","enctype":"json","params":{"username":{"help":"The TikTok user username","validate":"^([a-zA-Z0-9_.]+|https?://vm.tiktok.com/[a-zA-Z0-9]+/?)$","type":"string","required":True,"example":"lilyachty"},"secUid":{"validate":"^(.*?){30,}$","help":"The TikTok user secUid. You can get this from the <a href='#tag/Public/operation/public.check'>Get profile information</a> endpoint using the username.","type":"string","example":"MS4wLjABAAAAsHntXC3s0AvxcecggxsoVa4eAiT8OVafVZ4OQXxy-9htpnUi0sOYSr0kGGD1Loud","required":True},"user_id":{"help":"The TikTok user ID","type":"string","validate":"^[0-9]+$","required":True,"example":"6569595380449902597"}},"$other":{"openapi":{"hide":True,"fields":{"deprecated":True,"tags":["Followers"],"security":[{"apiKey":[],"accountKey":["follow_actions"]}]}}}}, cls.__get_options__(), "User.follow")(username=username, secUid=secUid, user_id=user_id, **otherParams)
	
		@classmethod
		def unfollow(cls, username: str = None, secUid: str = None, user_id: str = None, **otherParams) -> APIResponse:
			'''
				Unfollow a user 
			'''
			
			return wrap({"help":"Unfollow a user","comment":"*This endpoint is only available to trusted customers. \n<a target=\"_blank\" href='https://helpdesk.tikapi.io/portal/en/kb/articles/how-can-i-get-access-to-special-endpoints'> Learn more about special endpoints</a>*\n\n<br>This endpoint is deprecated and might not work as excpeted.","path":"/user/unfollow","method":"POST","enctype":"json","params":{"username":{"help":"The TikTok user username","validate":"^([a-zA-Z0-9_.]+|https?://vm.tiktok.com/[a-zA-Z0-9]+/?)$","type":"string","required":True,"example":"lilyachty"},"secUid":{"validate":"^(.*?){30,}$","help":"The TikTok user secUid. You can get this from the <a href='#tag/Public/operation/public.check'>Get profile information</a> endpoint using the username.","type":"string","example":"MS4wLjABAAAAsHntXC3s0AvxcecggxsoVa4eAiT8OVafVZ4OQXxy-9htpnUi0sOYSr0kGGD1Loud","required":True},"user_id":{"help":"The TikTok user ID","type":"string","validate":"^[0-9]+$","required":True,"example":"6569595380449902597"}},"$other":{"openapi":{"hide":True,"fields":{"deprecated":True,"tags":["Followers"],"security":[{"apiKey":[],"accountKey":["follow_actions"]}]}}}}, cls.__get_options__(), "User.unfollow")(username=username, secUid=secUid, user_id=user_id, **otherParams)
	
		posts = Rests.UserPosts
		@classmethod
		def conversations(cls, nextCursor: int = None, **otherParams) -> APIResponse:
			'''
				Get user conversations 
			'''
			
			return wrap({"path":"/user/conversations","help":"Get user conversations","comment":"**Premium**<img title='Only Business and Enterprise subscriptions can access this\nendpoint' style='margin-bottom: -3px;cursor: help;'\nsrc='/assets/img/star.png' width='18px'><br/>\nGet a list of current user conversations including the latest messages","params":{"nextCursor":{"help":"The starting offset of items list. Returned in every response, should be included in the next request for iteration.<br><br> *(A simple iteration method is already implemented in the Javascript & Python libraries as seen in the request samples)*","type":"number","validate":"^[0-9]+$"}},"$other":{"openapi":{"fields":{"tags":["Messages"],"security":[{"apiKey":[],"accountKey":["view_messages"]}]}}},"method":"GET"}, cls.__get_options__(), "User.conversations")(nextCursor=nextCursor, **otherParams)
	
		@classmethod
		def messages(cls, conversation_id = None, conversation_short_id = None, nextCursor: str = None, limit = None, **otherParams) -> APIResponse:
			'''
				Get user messages 
			'''
			
			return wrap({"path":"/user/messages","help":"Get user messages","comment":"**Premium**<img title='Only Business and Enterprise subscriptions can access this\nendpoint' style='margin-bottom: -3px;cursor: help;'\nsrc='/assets/img/star.png' width='18px'><br/>\nGet full messages list of a conversation","params":{"conversation_id":{"help":"The conversation ID","required":True,"example":"0:1:684574219823284956:69402435203845897564"},"conversation_short_id":{"help":"The additional conversation short ID (TikTok uses two different ID's for some reason)","required":True,"example":"6940245147502654884"},"nextCursor":{"help":"The starting point of the items list. Returned in every response, should be included in the next request for iteration.<br><br> *(A simple iteration method is already implemented in the Javascript & Python libraries as seen in the request samples)*","type":"string","validate":"^[0-9]+$"},"limit":{"validate":"^[0-9]{1,2}$"}},"$other":{"openapi":{"fields":{"tags":["Messages"],"security":[{"apiKey":[],"accountKey":["view_messages"]}]}}},"method":"GET"}, cls.__get_options__(), "User.messages")(conversation_id=conversation_id, conversation_short_id=conversation_short_id, nextCursor=nextCursor, limit=limit, **otherParams)
	
		@classmethod
		def sendMessage(cls, text: str = None, conversation_id: str = None, conversation_short_id: str = None, ticket: str = None, **otherParams) -> APIResponse:
			'''
				Send a message 
			'''
			
			return wrap({"path":"/user/message/send","help":"Send a message","comment":"**Premium**<img title='Only Business and Enterprise subscriptions can access this\nendpoint' style='margin-bottom: -3px;cursor: help;'\nsrc='/assets/img/star.png' width='18px'><br/>\n*This endpoint is only available to trusted customers. \n<a target=\"_blank\" href='https://helpdesk.tikapi.io/portal/en/kb/articles/how-can-i-get-access-to-special-endpoints'> Learn more about special endpoints</a>*\n\n","method":"POST","params":{"text":{"required":True,"type":"string","help":"The message text","example":"Hey! How you doing?"},"conversation_id":{"help":"The conversation ID","required":True,"type":"string","example":"0:1:684574219823284956:69402435203845897564"},"conversation_short_id":{"help":"The additional conversation short ID (TikTok uses two different ID's for some reason)","required":True,"type":"string","example":"6940245147502654884"},"ticket":{"help":"The conversation ticket","required":True,"type":"string","example":"3M8IlBpABq00h2aNB1B5JJ2ne0DTnGLLAFjGQQGMf4BKWJxEYxf7RAE0KaD2EjkQkWiJalT4xj36JGWa1ZmQg7SgQfHLoXffNFYLkIJhe1HVyiPXitoxWFyuzlX1xvBCYhZxkQALHE4gx9AaXBPEZjks7jC"}},"$other":{"openapi":{"fields":{"tags":["Messages"],"security":[{"apiKey":[],"accountKey":["send_messages"]}]}}}}, cls.__get_options__(), "User.sendMessage")(text=text, conversation_id=conversation_id, conversation_short_id=conversation_short_id, ticket=ticket, **otherParams)
	
		conversationRequests = Rests.UserConversationRequests
		live = Rests.UserLive
	Rests.User = User
	class API(Rests.BaseClass):
		

		__options__ = {}

		def __new__(self, apiKey = None, **values) -> 'API':
			'''
				Initialize new instance with default values & options for all requests
			'''
			return super().__new__(self, apiKey=apiKey, **values)

		@classmethod
		def set(self, apiKey = None, **values) -> 'API':
			'''
				Set default values & options for 'API'
			'''
			return super().set(apiKey=apiKey, **values)
	
		public = Rests.Public
		user = Rests.User
		@classmethod
		def key(cls, **otherParams) -> APIResponse:
			'''
				Get information about your API Key 
			'''
			
			return wrap({"path":"/key/info","help":"Get information about your API Key","$other":{"openapi":{"fields":{"tags":["Key"]}}},"method":"GET","params":{}}, cls.__get_options__(), "Key")(**otherParams)
	
		__Rests__ = Rests
	Rests.API = API
	return API