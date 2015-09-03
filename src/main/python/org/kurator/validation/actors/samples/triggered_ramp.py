
def ramp(end):
    print 'triggered_ramp.py: end=%s' % end
    for value in range(1, end + 1):
        yield value
