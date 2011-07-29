"""Bash color."""

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(30, 38)
RESET = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
DARK_SEQ = "\033[0;%dm"


def yellow(t):
	return '%s%s%s' % (COLOR_SEQ % YELLOW, t, RESET)

def red(t):
	return '%s%s%s' % (COLOR_SEQ % RED, t, RESET)

def green(t):
	return '%s%s%s' % (COLOR_SEQ % GREEN, t, RESET)

def blue(t):
	return '%s%s%s' % (COLOR_SEQ % BLUE, t, RESET)

def cyan(t):
	return '%s%s%s' % (COLOR_SEQ % CYAN, t, RESET)
