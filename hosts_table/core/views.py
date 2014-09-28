import os
import json

from django.shortcuts import render
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

import dmidecode

from core.models import Raw, Host


SERVER = 'http://huanghao-pc.bj.intel.com:8000'
DELIMITER = 'a_123454321_a'
CODE_VERSION = '0.2'
CODE = open(os.path.join(os.path.dirname(__file__), 'collect.sh')).read()


def version(request):
    return HttpResponse(CODE_VERSION, content_type='text/plain')


def collect(request):
    code = CODE % {
        'version': CODE_VERSION,
        'collect_url': SERVER + reverse('collect'),
        'version_url': SERVER + reverse('version'),
        'upload_url': SERVER + reverse('upload'),
        'delimiter': DELIMITER,
        }
    return HttpResponse(code, content_type="text/plain")


@require_POST
@csrf_exempt
def upload(request):
    try:
        ip = request.META['REMOTE_ADDR']

        data = {}
        for sec in request.body.strip().split(DELIMITER):
            typ, content = sec.strip().split('\n', 1)
            data[typ] = content.strip()

        raw, _ = Raw.objects.get_or_create(ip=ip)
        raw.data = json.dumps(data)
        raw.save()

        # TODO: async
        update_host(ip, data)
    except Exception as err:
        import traceback
        traceback.print_exc()
    return HttpResponse('Done', content_type='text/plain')



def parse_df(content):
    '''
Filesystem     Type 1G-blocks  Used Available Use% Mounted on
/dev/sda1      ext4      910G  230G      634G  27% /
    '''
    lines = content.strip().splitlines()
    total = 0
    for line in lines[1:]:
        size = line.split()[2]
        total += int(size.rstrip('G'))
    return '%dG' % total 


def update_host(ip, data):
    hostname = data['hostname']
    disk_size = parse_df(data['df'])
    dmi = dmidecode.humanize(dmidecode.parse_dmi(data['dmidecode']))
    host, _ = Host.objects.get_or_create(uuid=dmi['uuid'])
    host.sn = dmi['sn']
    host.hostname = hostname
    host.ip = ip
    host.model = dmi['model']
    host.cpus = dmi['cpus']
    host.memory = dmi['memory']
    host.disk = disk_size
    host.slots = dmi['slots']
    host.save()


def index(request):
    hosts = Host.objects.all()
    return render(request, 'core/index.html', {
            'hosts': hosts,
            })


def raw(request, ip):
    try:
        raw = Raw.objects.get(ip=ip)
    except Raw.DoesNotExist:
        return "Not found"
    return render(request, 'core/raw.html', {
            'data': json.loads(raw.data),
            })
