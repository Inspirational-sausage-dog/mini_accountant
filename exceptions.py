""" Custom exceptions """


class NotCorrectMessageException(Exception):
    """ Message is incorrect and couldn't go throw parsing """
    pass

class CategoryDoesNotExistException(Exception):
    """ Category does not exist """
    pass
