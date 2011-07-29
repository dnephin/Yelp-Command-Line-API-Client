"""
Command line yelp.
"""
import string
import auth
import color

command_help = """
Commands:
  search - find cool local businesses
  			ex: search pizza in san francisco
			    search bars in 94106
  help   - this list of commands
  quit   - quit
"""


class State(object):

	def process_input(self, input):
		parts = [part.strip() for part in input.split(' ', 1)]
		input = None if len(parts) == 1 else ' '.join(parts[1:])
		return self.handle_input(parts[0], input)

class BizState(State):

	@classmethod
	def start(cls, search_state, biz_details):
		state = cls()
		state.prev_state = search_state
		state.details = biz_details
		state._details(biz_details['id'])
		return state, None

	def menu(self):
		d = self.details
		loc = d['location']
		return '\n' + '\n'.join([
			color.cyan('Name: %s' % d['name']),
			'Address: %s' % ', '.join(loc['display_address']),
			'Phone: %s' % d.get('display_phone') or d.get('phone', ''),
			'Reviews: %s' % d['review_count'],
			'Text: %s' % d.get('snippet_text'),
		]) + '\n' + self._format_review()

	def prompt(self):
		return 'more (next/prev/return): '

	def handle_input(self, input, _):
		if input in ('return', 'no', 'n', 'N', 'No'):
			return self.prev_state, None

		if input == 'next' and self._current_review < len(self.reviews['reviews']) - 1:
			self._current_review += 1
			return self, None

		if input == 'prev' and self._current_review > 0:
			self._current_review -= 1
			return self, None

		if input in ('prev', 'next'):
			return self, 'That\'s it!'

		return self, 'Say what?'

	def _details(self, biz_id):
		self.reviews = auth.reviews(biz_id)
		self._current_review = 0

	def _format_review(self):
		if not self.reviews['reviews']:
			return ''
		review = self.reviews['reviews'][self._current_review]
		return '%s\n User: %s\n Rating: %s\n Review: %s\n' % (
			color.green('Review'),
			color.cyan(review['user']['name']),
			color.yellow('*' * review['rating']),
			review['excerpt']
		)


class SearchState(State):

	limit = 20

	@classmethod
	def start(cls, terms):
		state = cls()
		if not terms:
			return DefaultState.instance(), 'Please specify a search term, e.g. "search pizza in soma"'
		parts = [part.strip() for part in terms.split(' in ', 2)]
		if len(parts) != 2:
			return DefaultState.instance(), 'I couldn\'t understand "%s".' % terms
		state.offset = 0
		state.term = parts[0]
		state.loc = parts[1]
		results = state._search(state.term, state.loc)
		if not state.results:
			return DefaultState.instance(), 'No results.'
		return state, None
		
	def menu(self):
		return 'Total search results: %d\n%s' % (
			self.total,
			self._format_results()
		)

	def prompt(self):
		return 'search (next/prev/return/#): '
	
	def handle_input(self, input, extra):
		if input == 'return':
			return DefaultState.instance(), None
		if input.isdigit():
			idx = int(input)
			if idx < 0 or idx >= len(self.results):
				return self, 'Nope, that\' not in the list of results.'
			return BizState.start(self, self.results[idx])
		if input == 'next':
			self.offset += self.limit
			self._search(self.term, self.loc, offset=self.offset)
			return self, 'More...'
		if input == 'prev' and self.offset > 0:
			self.offset -= self.limit
			self._search(self.term, self.loc, offset=self.offset)
			return self, 'Prev page...'

		return DefaultState.instance(), 'Really?'

	def _search(self, term, loc, offset=0):
		result_dict = auth.search(term, loc, offset=offset)
		self.results = result_dict.get('businesses') or []
		self.total = result_dict.get('total') or 0

	def _format_results(self):
		formatted_biz = []
		for idx, biz in enumerate(self.results):
			cat_string = ''
			if biz.get('categories'):
				cat_string = '(%s)' % (','.join(cat[0] for cat in biz['categories']))
			formatted_biz.append(
				"%2d. %-45s %-30s %s" % (idx, 
					color.cyan(biz['name'][:29]),
					biz['location']['address'][0][:29] if biz['location']['address'] else '',
					cat_string
				)
			)
		return '\n'.join(formatted_biz)


class DefaultState(State):

	__instance = None

	@classmethod
	def instance(cls):
		if not cls.__instance:
			cls.__instance = DefaultState()
		return cls.__instance

	def menu(self):
		return 'Enter a command.'

	def prompt(self):
		return 'yelp: '
	
	def handle_input(self, input, extra):
		if input == 'quit':
			return None, 'Bye'
		if input == 'help':
			return self, command_help
		if input == 'search':
			return SearchState.start(extra)

		return self, "I didn't get that. Say again?\n"

__global_state = DefaultState.instance()


if __name__ == '__main__':

	while True:
		print __global_state.menu()
		input = raw_input(color.blue(__global_state.prompt()))
		__global_state, msg = __global_state.process_input(input)
		if msg:
			print color.red(msg)
		if not __global_state:
			break
