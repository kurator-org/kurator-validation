# actor parameters
term='year'
value='1990'
include=True

def filter(occurrence):
  global term
  global value
  global include
  if include==True:
    if (occurrence[term]==value):
      return occurrence
    else:
      return None
  else:
    if (occurrence[term]==value):
      return None
    else:
      return occurrence