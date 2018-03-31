import re

def between_markers(text: str, begin: str, end: str) -> str:
    """
        returns substring between two given markers
    """
    # your code here
    if re.findall('%s(.*?)%s' %(begin, end), text):
        return re.findall('%s(.*?)%s' %(begin, end), text)[0]
    elif re.findall('^(.*?)%s' %end, text):
        return re.findall('^(.*?)%s' %end, text)[0]
    elif re.findall('%s(.*?)$' %begin, text):
        return re.findall('%s(.*?)$' %begin, text)[0]
    return ''


if __name__ == '__main__':
    # These "asserts" are used for self-checking and not for testing
    assert between_markers('What is >apple<', '>', '<') == "apple", "One sym"
    assert between_markers("<head><title>My new site</title></head>",
                           "<title>", "</title>") == "My new site", "HTML"
    assert between_markers('No[/b] hi', '[b]', '[/b]') == 'No', 'No opened'
    assert between_markers('No [b]hi', '[b]', '[/b]') == 'hi', 'No close'
    assert between_markers('No hi', '[b]', '[/b]') == 'No hi', 'No markers at all'
    assert between_markers('No <hi>', '>', '<') == '', 'Wrong direction'
    print('Wow, you are doing pretty good. Time to check it!')
