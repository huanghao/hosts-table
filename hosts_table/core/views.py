import os
import json

from django.shortcuts import render
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

import dmidecode

from core.models import HostInfo


SERVER = 'http://huanghao-pc.bj.intel.com:8000'
DELIMITER = 'a_123454321_a'
CODE_VERSION = '0.1'
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
    client_ip = request.META['REMOTE_ADDR']
    info = {}
    for sec in request.body.strip().split(DELIMITER):
        typ, content = sec.strip().split('\n', 1)
        if typ == 'hostname':
            info[typ] = content.strip()
        elif typ == 'dmidecode':
            info[typ] = dmidecode.parse_dmi(content.strip())

    host, _ = HostInfo.objects.get_or_create(ip=client_ip)
    host.data = json.dumps(info)
    host.save()

    return HttpResponse('Done', content_type='text/plain')


def index(request):
    def _trans(host):
        data = host.data = json.loads(host.data)
        info = {
            'ip': host.ip,
            'hostname': data['hostname'],
            'updated': host.updated,
            }

        cnt, total, unit = 0, 0, None
        for typ, val in data['dmidecode']:
            if typ == 'system':
                info['system'] = '%s %s '% (
                    val['Manufacturer'],
                    val['Product_Name'],
                    )
            elif typ == 'memory_device':
                if val['Size'] == 'No Module Installed':
                    continue
                i, unit = val['Size'].split()
                cnt += 1
                total += int(i)
            elif typ == 'processor':
                info['cpu'] = '%s %s %s' % (
                    val['Manufacturer'],
                    val['Family'],
                    val['Max_Speed'],
                    )
                if 'Core_Count' in val:
                    info['cpu'] += ' (Core: %s, Thead: %s)' % (
                        val['Core_Count'],
                        val['Thread_Count'],
                        )

        info['memory'] = '%d memory stick(s), %d %s' % (
            cnt,
            total,
            unit,
            )

        return info

    hosts = [_trans(i) for i in HostInfo.objects.all()]
    return render(request, 'core/index.html', {
            'hosts': hosts,
            })


def host(reuqest, ip):
    try:
        host = HostInfo.objects.get(ip=ip)
    except HostInfo.DoesNotExist:
        return "Not found"
    return HttpResponse(host.data, content_type='application/json')
