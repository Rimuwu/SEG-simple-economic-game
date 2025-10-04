import string


class SafeFormatter(string.Formatter):
    def get_value(self, key, args, kwargs):
        if isinstance(key, str):
            if key in kwargs:
                return kwargs[key]
            else:
                return '{' + key + '}'
        else:
            return super().get_value(key, args, kwargs)