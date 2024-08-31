from core.builtins import Bot
from core.component import module
from core.utils.http import get_url

from datetime import datetime

obastatus = module(
    bind_prefix='obastatus',
    desc='{obastatus.help.desc}',
    alias='oba',
    developers=['WorldHim'],
    support_languages=['zh_cn'],
)

def sizeConvert(value):
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
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

    message = f'''
    {msg.locale.t('obastatus.message.status.currentNodes', currentNodes = dashboard['currentNodes'])} | {msg.locale.t('obastatus.message.status.load', load = round(dashboard['load'] * 100, 2))}
    {msg.locale.t('obastatus.message.status.bandwidth', bandwidth = dashboard['bandwidth'])} | {msg.locale.t('obastatus.message.status.currentBandwidth', currentBandwidth = round(dashboard['currentBandwidth'], 2))}
    {msg.locale.t('obastatus.message.status.hits', hits = dashboard['hits'])} | {msg.locale.t('obastatus.message.status.bytes', size = sizeConvert(dashboard['bytes']))}
    {msg.locale.t('obastatus.message.queryTime', queryTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}
    '''

    await msg.finish(message)

@obastatus.command('rank [<rank>] {{obastatus.help.rank}}')
async def rank(msg: Bot.MessageSession, rank: int = 1):
    rankList = await get_url('https://bd.bangbang93.com/openbmclapi/metric/rank',
                             fmt='json')
    cluster = rankList[rank - 1]

    message = f'''
    {msg.locale.t('obastatus.message.rank.name', name = cluster['name'])}
    {msg.locale.t('obastatus.message.rank.id', id = cluster['_id'])}
    {msg.locale.t('obastatus.message.rank.hits', hits = cluster['metric']['hits'])}
    {msg.locale.t('obastatus.message.rank.size', size = sizeConvert(cluster['metric']['bytes']))}
    {msg.locale.t('obastatus.message.queryTime', queryTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S"))}
    '''

    await msg.finish(message)

@obastatus.command('version {{obastatus.help.version}}')
async def version(msg: Bot.MessageSession):
    await msg.finish(msg.locale.t('obastatus.message.version', version = await latestVersion()))