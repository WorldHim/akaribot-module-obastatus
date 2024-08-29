from core.builtins import Bot
from core.component import module
from core.utils.http import get_url

import datetime

obastatus = module(
    bind_prefix='obastatus',
    desc='{obastatus.help.desc}',
    alias='oba',
    developers=['WorldHim'],
    support_languages=['zh_cn'],
)

def hum_convert(value):
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    size = 1024.0
    for i in range(len(units)):
        if(value / size) < 1:
            return "%.2f%s" % (value, ' ' + units[i])
        value /= size

async def latestVersion():
    version = await get_url('https://bd.bangbang93.com/openbmclapi/metric/version',
                           fmt='json')
    return version['version'] + '@' + version['_resolved'].split('#')[1][:7]

@obastatus.command('{{obastatus.help.status}}')
@obastatus.command('status {{obastatus.help.status}}')
async def status(msg: Bot.MessageSession):
    dashboard = await get_url('https://bd.bangbang93.com/openbmclapi/metric/dashboard',
                             fmt='json')
    message = msg.locale.t('obastatus.message.status.currentNodes', currentNodes = dashboard['currentNodes']) + ' | ' + msg.locale.t('obastatus.message.status.load', load = round(dashboard['load'] * 100, 2))
    message += '\n'
    message += msg.locale.t('obastatus.message.status.bandwidth', bandwidth = dashboard['bandwidth']) + ' | ' + msg.locale.t('obastatus.message.status.currentBandwidth', currentBandwidth = round(dashboard['currentBandwidth'], 2))
    message += '\n'
    message += msg.locale.t('obastatus.message.status.hits', hits = dashboard['hits']) + ' | ' + msg.locale.t('obastatus.message.status.bytes', bytes = hum_convert(dashboard['bytes']))
    message += '\n'
    message += msg.locale.t('obastatus.message.status.queryTime', queryTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    await msg.finish(message)

@obastatus.command('version {{obastatus.help.version}}')
async def version(msg: Bot.MessageSession):
    await msg.finish(msg.locale.t('obastatus.message.version') + await latestVersion())