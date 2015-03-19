
def is_blank(s):
    return len(s.strip()) == 0

def has_content(s):
    return s != None and not is_blank(s)

class SpacedStringBuilder(object):

  def __init__(self, spacer=' ', quote='"'):
    self.str_list = []
    self._spacer = spacer
    self.quote = quote
  
  def append(self, s):
    if has_content(s):
      self.str_list.append(s)
    return self

  def append_quoted(self, s): 
    if has_content(s):
        self.str_list.append(self.quote + s + self.quote)
    return self

  def __repr__(self):
    return self._spacer.join(self.str_list)

