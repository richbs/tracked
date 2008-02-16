import re, django
from django.utils.translation import ugettext_lazy, ungettext
from django.utils.functional import Promise, lazy
from django.utils.encoding import force_unicode
from django.core.validators import ValidationError

lazy_inter = lazy(lambda a,b: force_unicode(a) % b, unicode)

class FilenameMatchesRegularExpression(object):
    """
    Checks that the filename field matches the given regular-expression. The regex
    should be in string format, not already compiled.
    """
    def __init__(self, regexp, error_message=ugettext_lazy("The format for this field is wrong.")):
        self.regexp = re.compile(regexp)
        self.error_message = error_message

    def __call__(self, field_data, all_data):
        if type(field_data) == unicode:
            string_to_validate = field_data
        elif type(field_data) == django.utils.datastructures.FileDict:
            string_to_validate = field_data['filename']
        else:
            assert False, type(field_data)
        if not self.regexp.search(string_to_validate):
            raise ValidationError(self.error_message)

class HasAllowableSize(object):
    """
    Checks that the file-upload field data is a certain size. min_size and
    max_size are measurements in bytes.
    """
    def __init__(self, min_size=None, max_size=None, min_error_message=None, max_error_message=None):
        self.min_size, self.max_size = min_size, max_size
        self.min_error_message = min_error_message or lazy_inter(ugettext_lazy("Make sure your uploaded file is at least %s bytes big."), min_size)
        self.max_error_message = max_error_message or lazy_inter(ugettext_lazy("Make sure your uploaded file is at most %s bytes big."), max_size)

    def __call__(self, field_data, all_data):
        try:
            content = field_data['content']
        except TypeError:
            # Don't raise error if there's no content
            return True
            # raise ValidationError, ugettext_lazy("No file was submitted. Check the encoding type on the form.")
        if self.min_size is not None and len(content) < self.min_size:
            raise ValidationError, self.min_error_message
        if self.max_size is not None and len(content) > self.max_size:
            raise ValidationError, self.max_error_message
