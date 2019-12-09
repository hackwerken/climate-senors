import urequests

class Measurement:
    def __init__(self, name, tags={}, fields={}):
        self.name = name
        self.tags = tags
        self.fields = fields

    def __str__(self):
        return self.to_line_protocol()

    def to_line_protocol(self): 
        from uio import StringIO
        stream = StringIO()

        stream.write(self.name)
        stream.write(',')
        
        def formatDict(dict):
            first = True
            for key, value in dict.items():
                if not first:
                    stream.write(',')
                else:
                    first = False

                arg = '{0}={1}'.format(key, value)
                stream.write(arg)
        
        formatDict(self.tags)
        stream.write(' ')
        formatDict(self.fields)

        return stream.getvalue()

class Client:
    def __init__(self, name, endpoint):
        self.endpoint = endpoint
        self.name = name
    
    def insert(self, measurement):
        lineProtocol = measurement.to_line_protocol()
        
        headers = {'Accept': 'text/plain',
           'Connection': 'close',
           'Content-type': 'application/octet-stream'}
        response = urequests.post(self.endpoint,
                                  data=lineProtocol,
                                  headers=headers)
        response.close()