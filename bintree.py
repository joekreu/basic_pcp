''' This module defines a class that is meant to process a representation
    of a binary tree. In particular, a parse trees can be represented as a
    list of strings and printed.

    _ListOfLines             This class provides some function for processing
                             a list of text lines.
    FormatBinaryTree         A subclass of _ListOfLines.
                             Represent and 'pretty-print' a binary parse tree.


    Version: 0.2, 2022-02-14.
    Python 3.8 or higher (the 'walrus'-operator ':=' is used).
'''

# Characters for 'pretty-printing' of tree structures. They can be
# replaced with other graphical characters. To be used in 'FormatBinaryTree'.
_H_LINE_CHAR = chr(183)       # Vertically centered dot, used for h-lines
_SLASH_CHAR = "/"             # Forward slash
_BACKSLASH_CHAR = "\\"        # Backslash
# Possible alternatives: _SLASH_CHAR=chr(65295), _H_LINE_CHAR=chr(8213)
# The following is used for upside down representation of parse tress.
SWAPDIC = {_SLASH_CHAR: _BACKSLASH_CHAR, _BACKSLASH_CHAR: _SLASH_CHAR}


class _ListOfLines:
    ''' This class provides some function for processing a list of text lines.

        Text strings can be inserted at any position specified by linenum,
        col. Fill with empty lines, or with space characters, if required.
        The text content is stored in a list of lines (strings).
    '''

    def __init__(self):
        self.lines_count = 0
        self.lines = []   # Initialize the list of lines.

    def _add_lines(self, n_lines=1):
        ''' Add n_lines empty lines. '''
        self.lines = self.lines + [""]*n_lines
        self.lines_count += n_lines

    def insert_at(self, linenum, col, text):
        ''' Insert text into specific line at position linenum, col (both zero
            based). Overwrite existing text at that position, if any.
        '''
        if not text:    # Don't do anything if text is an empty string
            return
        if self.lines_count <= linenum:
            self._add_lines(linenum - self.lines_count + 1)
        line = self.lines[linenum]
        start = line[:col]
        rest = line[(col + len(text)):]
        padd = " "*(col - len(start))
        self.lines[linenum] = start + padd + text + rest

    def clear(self):
        ''' Clear content. (Not used for formatting of parse trees.) '''
        self.lines_count = 0
        self.lines = []

    def printall(self):
        ''' Print all lines. '''
        for line in self.lines:
            print(line)

    def upsidedown(self):
        ''' Reverse line order; replace slash by backslash and vice versa. '''

        self.lines.reverse()
        for linenum, line in enumerate(self.lines):
            self.insert_at(linenum, 0,
                           "".join([SWAPDIC.get(s, s) for s in list(line)]))


class FormatBinaryTree(_ListOfLines):
    ''' Format a binary tree. To be use for 'pretty printing' of parse trees.
    '''

    def __init__(self, btree, linenum=0):
        super().__init__()
        self.h_pos = 1
        self._add_tree(btree, linenum)

    def _add_tree(self, btree, linenum, reset_h_pos=False):
        ''' Recursively create a binary tree representation in a
            _ListOfLines instance (see above).
        '''

        if reset_h_pos:
            self.h_pos = 1

        if isinstance(btree, (str, int, float)):  # Atomic value?
            if not (sbt := str(btree)):
                raise ValueError("Empty element in binary tree")
            self.insert_at(linenum, self.h_pos, sbt)
            self.h_pos += len(sbt) + 1
            return
        if not 2 <= len(btree) <= 3:
            raise ValueError("Binary tree " + str(btree)[:20] +
                             " has invalid number of elements")
        if btree[1] != "$PRE":
            self._add_tree(btree[1], linenum+2)
            slash_h_pos = self.h_pos - 1
            self.insert_at(linenum + 1, slash_h_pos, _SLASH_CHAR)
            i = slash_h_pos - 1
            lin = self.lines[linenum+2]
            while i >= len(lin) or lin[i] == " ":
                self.insert_at(linenum+2, i, _H_LINE_CHAR)
                i -= 1

        if not (sbt := str(btree[0])):
            raise ValueError("Binary tree has empty operator")
        self.insert_at(linenum, self.h_pos, sbt)
        backslash_h_pos = self.h_pos + len(sbt)
        self.h_pos = backslash_h_pos + 1

        if not(len(btree) == 3 and btree[2] == "$POST"):
            t_tree = btree[2] if len(btree) == 3 else btree[1]
            self.insert_at(linenum + 1, backslash_h_pos, _BACKSLASH_CHAR)
            self._add_tree(t_tree, linenum+2)
            i = backslash_h_pos + 1
            while self.lines[linenum+2][i] == " ":
                self.insert_at(linenum+2, i, _H_LINE_CHAR)
                i += 1
