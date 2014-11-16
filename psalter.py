#!/usr/bin/python
import re
import urllib2

class Psalter:
    def __init__(self):
        self.psalms = {}
        self._bcp_cache = {}

    def _get_psalm(self, number):
        text = self._bcp_page_from_psalm_number(number)

        # First pare down to just the chapter we want:
        text = _extract_chapter(text, number)

        # then pretty it up:
        text = _remove_rubrics(text)
        text = _remove_page_numbers(text)
        text = _remove_markup(text)

        verse_a = re.findall(r'[0-9]+[^0-9]*\*', text, re.DOTALL)
        verse_b = re.findall(r'\*[^0-9]*', text, re.DOTALL)

        if len(verse_a) != len(verse_b):
            raise RuntimeError('Experienced a catastrophic (Zalgo) regex ' +
                               'failure.')

        psalm = Chapter('Psalm', number)

        for v in range(0, len(verse_a)):
            # keep prettying:
            psalm.add_verse(_bcp_clean(verse_a[v]), _bcp_clean(verse_b[v]))
        return psalm

    def psalm(self, psalm):
        if psalm not in self.psalms.keys():
            self.psalms[psalm] = self._get_psalm(psalm)
        return self.psalms[psalm]

    def prime_all(self):
        for i in range(1, 151, 10):
            self.prime(i)

    def prime(self, index):
        self._bcp_page_from_psalm_number(i)

    def _bcp_page_from_psalm_number(self, psalm):
        url = _bcpurl_from_psalm(psalm)
        if not self._bcp_cache.has_key(url):
            page = urllib2.urlopen(url)
            self._bcp_cache[url] = _fix_missing_anchors(page.read())
        return self._bcp_cache[url]

class Chapter:
    def __init__(self, book, number):
        self.book = book
        self.number = number
        self.verses = []

    def add_verse(self, fragment_a, fragment_b):
        self.verses.append(Verse(self.book, self.number, len(self.verses)+1,
                                  fragment_a, fragment_b))

    def __len__(self):
        return len(self.verses)

    def __str__(self):
        print_verses = []
        for v in self.verses:
            print_verses.append(str(v))
        return self.__repr__() + '\n' + '\n'.join(print_verses)

    def __repr__(self):
        return self.book + ' ' + str(self.number)

class Verse:
    def __init__(self, book, chapter, number,
                 fragment_a, fragment_b):
        self.book = book
        self.chapter = chapter
        self.number = number
        self.a = fragment_a
        self.b = fragment_b


    def __str__(self):
        return (str(self.number) + ' ' +
                self.a + ' *\n' +
                self.b)

    def __repr__(self):
        return self.book + ' ' + str(self.chapter) + ':' + str(self.number)

class TestError(Exception):
    pass

class AssertError(TestError):
    def __init__(self, case, expected, actual):
        self.case = case
        self.expected = expected
        self.actual = str(actual)

    def __repr__(self):
        return self.case

    def __str__(self):
        # Turns out string generators are obnoxious as all get out
        diff = unified_diff(self.expected.split('\n'), self.actual.split('\n'),
                            fromfile='expected', tofile='got', n=2, lineterm='')
        buf = str(self.case) + '\n'
        for line in diff:
            buf += line + '\n'
        return buf

class TestNotFoundError(TestError):
    def __init__(self, name, directory=False):
        self.name = str(name)
        if not directory:
            self.msg = ' is not a valid test.'
        else:
            self.msg = ' contains no valid tests.'

    def __str__(self):
        return self.name + self.msg

class InvalidTestError(TestError):
    def __init__(self, psalm):
        self.psalm = str(psalm)

    def __str__(self):
        return self.psalm + ' is not a valid BCP Psalter Psalm.'

def _bcpurl_from_psalm(psalm):
    bottom = (((psalm - 1)/ 10) * 10 + 1)
    top = bottom + 9
    return ('http://www.bcponline.org/Psalter/' +
           str(bottom) + '-' + str(top) +
           '.htm')

def _fix_missing_anchors(html):
    # lolololololololol
    # so technically, we could rewrite _extract_chapter to not use the anchor,
    # but it already works so screw that.
    return re.sub(r'<font size="6"><b>([0-9]+)&nbsp; </b>',
                  r'<font size="6"><b><a name="\1"></a>\1&nbsp; </b>',
                   html)

def _extract_chapter(text, psalm):
    # this was easier than getting the OR in the regex to work right:
    if psalm % 10 != 0:
        text = ''.join(re.findall('<a name="' + str(psalm) + '">(.*)<a name="' +
                                  str(psalm+1) + '">', text, re.DOTALL))
    else:
        text = ''.join(re.findall('<a name="' + str(psalm) + '">(.*)',
                                  text, re.DOTALL))
    return text

def _remove_rubrics(text):
    # deal with rubrics and latin blowing things up:
    text = re.sub(r'<font face="Goudy Old Style" size="2"><i>[^<]*</i></font>',
                  '', text)
    # lol, of course:
    text = re.sub(r'<i><font face="Goudy Old Style" size="2">[^<]*</font></i>',
                  '', text)
    return text

def _remove_page_numbers(text):
    # Oh God, this .*\n*.* pattern is so fragile:
    text = re.sub(r'<p align="right">.*\n*.*</p>', '', text, re.DOTALL)
    return text

def _remove_markup(text):
    # Newlines are still significant as whitespace
    text = re.sub(r'<br>', ' ', text)
    # Everything else can go. We don't need no stinkin' markup:
    text = re.sub(r'<[^<>]*>', '', text)

    # We don't do that for sanity's sake, but a subtler, more fiidly
    # approach might look like this:

    # text = re.sub(r'</?td[^>]*>', '', text)
    # text = re.sub(r'</?font[^>]*>', '', text)
    return text

def _bcp_clean(text):
    # I was pretty sure the order was important here.
    # Maybe it isn't, but I'm too afraid to change it

    # Verse numbers and asterisks can be reconstructed. The rest is garbage.
    text = re.sub(r'\r',    ' ', text)
    text = re.sub(r'\n',    ' ', text)
    text = re.sub(r'\t',    ' ', text)
    text = re.sub(r'\*',    ' ', text)
    text = re.sub(r'[0-9]+',' ', text)

    # Whitespace consolidation
    text = re.sub(r'&nbsp;',' ', text) # hrrrk
    text = re.sub(r' {2,}', ' ', text)

    # clean up stuff that doesn't belong on the ends:
    text = re.sub(r'^<br>', '', text)
    text = re.sub(r'<br>$', '', text)
    text = re.sub(r'^ ',    '', text)
    text = re.sub(r' $',    '', text)

    # some textual substitutions:
    text = re.sub(r'&quot;', '"', text)

    return text

########

def expand_directory(directory):
    test_files = []
    for entry in os.listdir(directory):
        entry = os.path.join(directory, entry)
        if os.path.isfile(entry):
            with open(entry, 'r') as f:
                if re.search(r'^# TESTCASE ([0-9]+)$', f.readline()):
                    test_files.append(entry)
    if len(test_files) == 0:
        raise TestNotFoundError(directory, directory=True)
    return test_files

def assert_equal(expected, actual, note=None):
    if(expected != str(actual)):
        raise AssertError(note, expected, actual)
    else:
        print('PASSED: ' + str(note))

def test_case(case):
    with open(case, 'r') as f:
        test_info = re.search(r'^# TESTCASE ([0-9]+)$', f.readline())
        if not test_info:
            return
        psalm = int(test_info.group(1))
        if psalm < 1 or 150 < psalm:
            raise InvalidTestError(psalm)
        expected = ''
        for line in f:
            if not re.search(r'^#.*$', line) and not re.search(r'^$', line):
                expected += line

    psalter = Psalter()
    assert_equal(expected, str(psalter.psalm(psalm)), psalm)

def print_usage(code):
    print 'Usage: ' + sys.argv[0] + ' <command>'
    print '''
Valid Commands:
  --bcp <psalms>      Print out the BCP translation for each specified psalm.
                          <psalms> is a space-delimited list of numbers 1-150
  --bcp-dump          Print out the entire BCP Psalter
  --count [psalms]    Print out the verse count of the specified psalms
                          [psalms] defaults to all of them, 1-150
  --test [cases]      Run --bcp and compare input against [cases].
                          [cases] defaults to the script's directory.
'''
    sys.exit(code)

def main():
    if '--help' in sys.argv or '-h' in sys.argv or len(sys.argv) == 1:
        print_usage(0)

    psalter = Psalter()
    if sys.argv[1] == '--bcp':
        for psalm in sys.argv[2:]:
            print
            print psalter.psalm(int(psalm))
    elif sys.argv[1] == '--bcp-dump':
        for i in range(1,151):
            print psalter.psalm(i)
    elif sys.argv[1] == '--count':
        if 2 < len(sys.argv):
            psalms = sys.argv[2:]
        else:
            psalms = range(1,151)
        for i in psalms:
            print str(i) + ': ' + str(len(psalter.psalm(int(i))))
    elif sys.argv[1] == '--test':
        if 2 < len(sys.argv):
            cases = sys.argv[2:]
        else:
            cases = [os.path.dirname(sys.argv[0])]

        new_cases = []
        for c in cases:
            c = os.path.abspath(c)
            if os.path.isdir(c):
                try:
                    new_cases.extend(expand_directory(c))
                except TestError as e:
                    print 'FAIL: ' + str(e)

        cases.extend(new_cases)

        for c in cases:
            c = os.path.abspath(c)
            if os.path.isfile(c):
                try:
                    test_case(c)
                except TestError as e:
                    print 'FAIL: ' + str(e)
    else:
        print_usage(1)

if '__main__' == __name__:
    import os
    import sys
    from difflib import unified_diff
    main()

# Psalms by length
#   2: [117]
#   3: [131, 133, 134]
#   4: [123]
#   5: [15, 43, 70, 93, 100, 125, 127]
#   6: [1, 13, 23, 53, 126, 128, 150]
#   7: [11, 14, 54, 67, 87, 110, 120, 142]
#   8: [3, 4, 12, 61, 82, 101, 114, 121, 124, 129, 130, 138]
#   9: [8, 20, 28, 47, 52, 98, 99, 113, 122, 137, 149]
#  10: [6, 24, 64, 75, 111, 112, 141, 146]
#  11: [16, 29, 32, 42, 46, 57, 58, 63, 95]
#  12: [2, 5, 26, 30, 36, 60, 62, 76, 84, 97, 143]
#  13: [21, 39, 41, 56, 65, 79, 85, 96, 108, 140]
#  14: [19, 27, 48, 148]
#  15: [17, 92, 144]
#  16: [81, 91]
#  17: [7, 40, 59, 86, 90]
#  18: [10, 45, 83, 88, 115, 132]
#  19: [51, 80, 116]
#  20: [9, 49, 66, 72, 77, 147]
#  21: [135, 145]
#  22: [25, 33, 34, 38, 103]
#  23: [50, 55, 74, 94]
#  24: [31, 71, 139]
#  26: [44, 136]
#  28: [35, 73, 102]
#  29: [118]
#  31: [109]
#  32: [22]
#  35: [68, 104]
#  36: [69]
#  40: [37]
#  43: [107]
#  45: [105]
#  48: [106]
#  50: [18]
#  52: [89]
#  72: [78]
# 176: [119]

# verse counts from biblegateway.com
# note that these don't agree with the BCP (which favors parallelism).
# cf Ps 133 and Ps 134
