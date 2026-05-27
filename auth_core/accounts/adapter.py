# accounts/adapter.py
from allauth.account.adapter import DefaultAccountAdapter

class NoMessagesAdapter(DefaultAccountAdapter):
    def add_message(self, request, level, message_template, message_context=None, extra_tags=''):
        # We leave this blank to suppress all default allauth messages
        pass