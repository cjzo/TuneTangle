import requests
import io
from tikapi.api import Rests, APIException, ResponseException, ValidationException

def TikAPI(apiKey: str):
	if not isinstance(apiKey, str):
		raise APIException("API Key is required.")
	
	def on_success(response: requests.Response, request: dict):
		
		def next_items():
			'''
				A convenient method to get the next batch of items, if the endpoint has iteration parameters (e.g cursor)
			'''
			body: dict = {}

			try:
				body = response.json()
			except:
				return None

			nextCursorParams = {}

			if body.get("hasMore") or body.get("has_more"):
				nextCursor = body.get("offset", body.get("cursor", body.get("nextCursor")))
				if not nextCursor:
					return None
				
				nextCursorParams = {
					'cursor': nextCursor,
					'offset': nextCursor,
					'nextCursor': nextCursor
				}
			
			elif body.get('notice_lists'):
				notice_lists = body.get('notice_lists')

				if not isinstance(notice_lists, (list, tuple)) or not len(notice_lists):
					return None
				
				notice_body = notice_lists[0]

				if not notice_body.get('has_more'):
					return None

				minTime = notice_body.get('min_time') 
				maxTime = notice_body.get('max_time')

				
				if not minTime or not maxTime:
					return None

				nextCursorParams = {
					'min_time': minTime,
					'max_time': maxTime
				}
				 
			elif body.get('nextCursor'):
				nextCursorParams = {
					'nextCursor': body.get('nextCursor')
				}
			else:
				return None

			return request.get('self')(**{
				**request.get('params', {}),
				**nextCursorParams
			})

		def save_video(link: str, path: str, **requestKwargs):
			'''
				A method for downloading and saving videos.
			'''
			body: dict = response.json()
			headers = {
				"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
			}

			if body.get("$other") and isinstance(body["$other"].get("videoLinkHeaders"), dict):
				headers = {
					**headers,
					**body["$other"]["videoLinkHeaders"]
				}

			with requests.get(link, stream=True, headers=headers, **requestKwargs) as get_video:
				if get_video.status_code != 200:
					exception = ResponseException("Failed downloading video, received invalid status code: %s" % get_video.status_code)
					exception.response = get_video
					raise exception

				video_bytes = io.BytesIO(get_video.content)
				with open(path, "wb") as video_file:
					video_file.write(video_bytes.getbuffer())

			return True
			
		setattr(response, 'next_items', next_items)
		setattr(response, 'save_video', save_video)

	def on_error(error, request:dict):

		if hasattr(error, 'response'):
			message = str(error)

			try:
				message = error.response.json().get("message", str(error))
			except Exception as e:
				pass

			exception = ResponseException(message)

			exception.response = error.response

			raise exception

	instance = Rests({
		'values': {
			'apiKey': apiKey
		},
		'on_success': on_success,
		'on_error': on_error
	})

	return instance



__all__ = ['TikAPI', 'APIException', 'ResponseException', 'ValidateException']