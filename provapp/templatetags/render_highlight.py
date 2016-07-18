#! /usr/bin/env python
# -*- coding: utf-8 -*-
from django import template
register = template.Library()

# Pygments: http://pygments.org -- a generic syntax highlighter.
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer

# Python Markdown (dropped in my project directory)
from markdown import markdown

# BeautifulSoup: http://www.crummy.com/software/BeautifulSoup/
from BeautifulSoup import BeautifulSoup

@register.filter
def render(content, safe="unsafe"):
    """Render this content for display."""

    # First, pull out all the <code></code> blocks, to keep them away
    # from Markdown (and preserve whitespace).
    soup = BeautifulSoup(unicode(content))
    code_blocks = soup.findAll(u'code')
    for block in code_blocks:
        block.replaceWith(u'<code class="removed"></code>')

    # Run the post through markdown.
    if safe == u"unsafe":
        safe_mode = False
    else:
        safe_mode = True
    markeddown = markdown(unicode(soup), safe_mode=safe_mode)

    # Replace the pulled code blocks with syntax-highlighted versions.
    soup = BeautifulSoup(markeddown)
    empty_code_blocks, index = soup.findAll(u'code', u'removed'), 0
    formatter = HtmlFormatter(cssclass=u'source')
    for block in code_blocks:
        if block.has_key(u'class'):
            # <code class='python'>python code</code>
            language = block[u'class']
        else:
            # <code>plain text, whitespace-preserved</code>
            language = u'text'
        try:
            lexer = get_lexer_by_name(language, stripnl=True, encoding=u'UTF-8')
        except ValueError, e:
            try:
                # Guess a lexer by the contents of the block.
                lexer = guess_lexer(block.renderContents())
            except ValueError, e:
                # Just make it plain text.
                lexer = get_lexer_by_name(u'text', stripnl=True, encoding=u'UTF-8')
        empty_code_blocks[index].replaceWith(
                highlight(block.renderContents(), lexer, formatter))
        index = index + 1

