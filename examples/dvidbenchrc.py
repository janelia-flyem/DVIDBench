import random

class DVIDConfig:

    wait = 1000

    def url(self):
        x = random.choice(range(27,85))
        y = random.choice(range(27,85))
        z = random.choice(range(1540,1694))

        url = ("http://my.dvid.server:8000/api/node/1230517ccbe5417b9766a03133149adc/foo.jpg/tile/xy/1/{0}_{1}_{2}".format(x, y, z))

        return url


