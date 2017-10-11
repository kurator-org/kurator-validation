import uuid
import os

def on_start(options):
    print 'Started MakeWorkspace'
    print 'MakeWorkspace options: %s' % options
    if options.has_key('workspace') == False:
        options['workspace'] ='./workspace_'+str(uuid.uuid1())
        if not os.path.exists(options['workspace']):
            os.makedirs(options['workspace'])
    return options