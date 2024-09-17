from core.builtins import Bot, Image, Plain
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
            return '%.2f%s' % (value, ' ' + units[i])
        value /= size

async def latestVersion():
    version = await get_url('https://bd.bangbang93.com/openbmclapi/metric/version',
                            fmt='json')
    return f'''{version.get('version')}@{version.get('_resolved').split('#')[1][:7]}'''

@obastatus.command('{{obastatus.help.status}}')
@obastatus.command('status {{obastatus.help.status}}')
async def status(msg: Bot.MessageSession):
    dashboard = await get_url('https://bd.bangbang93.com/openbmclapi/metric/dashboard',
                              fmt='json')

    message = f'''{msg.locale.t('obastatus.message.status',
                                currentNodes = dashboard.get('currentNodes'),
                                load = round(dashboard.get('load') * 100, 2),
                                bandwidth = dashboard.get('bandwidth'),
                                currentBandwidth = round(dashboard.get('currentBandwidth'), 2),
                                hits = dashboard.get('hits'),
                                size = sizeConvert(dashboard.get('bytes')))}
{msg.locale.t('obastatus.message.queryTime', queryTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}'''

    await msg.finish(message)

@obastatus.command('rank [<rank>] {{obastatus.help.rank}}')
async def rank(msg: Bot.MessageSession, rank: int = 1):
    rankList = await get_url('https://bd.bangbang93.com/openbmclapi/metric/rank',
                             fmt='json')
    cluster = rankList[rank - 1]

    message = f'''{'🟩' if cluster.get('isEnabled') else '🟥'}
{msg.locale.t('obastatus.message.cluster',
              name = cluster.get('name'),
              id = cluster.get('_id'),
              hits = cluster.get('metric').get('hits'),
              size = sizeConvert(cluster.get('metric').get('bytes')))}
{msg.locale.t('obastatus.message.queryTime', queryTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}'''

    if 'sponsor' not in cluster:
        await msg.finish(message)
    else:
        msg.send_message(message)
        sponsor = cluster.get('sponsor')

        message = msg.locale.t('obastatus.message.sponsor',
                               name = sponsor.get('name'),
                               url = sponsor.get('url'))

        try:
            await msg.finish([Plain(message), Image(str(sponsor.get('banner')))])
        except Exception:
            await msg.finish(message)

@obastatus.command('top [<rank>] {{obastatus.help.top}}')
async def top(msg: Bot.MessageSession, rank: int = 10):
    rankList = await get_url('https://bd.bangbang93.com/openbmclapi/metric/rank',
                             fmt='json')

    cluster = rankList[0]

    sponsor_name = cluster.get('sponsor', '未知').get('name')
    message = '🟩| ' if cluster.get('isEnabled') else '🟥| ' 
    message += msg.locale.t('obastatus.message.top',
                            rank = 1,
                            name = cluster.get('name'),
                            id = cluster.get('_id'),
                            hits = cluster.get('metric').get('hits'),
                            size = sizeConvert(cluster.get('metric').get('bytes')),
                            sponsor_name = sponsor_name)

    for rank, cluster in enumerate(rankList):
        message += '\n'

        sponsor_name = cluster.get('sponsor', '未知').get('name')

        try:
            message += msg.locale.t('obastatus.message.top',
                                    rank = rank,
                                    name = cluster.get('name'),
                                    id = cluster.get('_id'),
                                    hits = cluster.get('metric').get('hits'),
                                    size = sizeConvert(cluster.get('metric').get(['bytes'])),
                                    sponsor_name = sponsor_name)
        except KeyError:
            break

    await msg.finish(message)

@obastatus.command('sponsor {{obastatus.help.sponsor}}')
async def sponsor(msg: Bot.MessageSession):
    sponsor = await get_url('https://bd.bangbang93.com/openbmclapi/sponsor',
                            fmt='json')
    cluster = await get_url('https://bd.bangbang93.com/openbmclapi/sponsor/' + str(sponsor['_id']),
                            fmt='json')
    message = msg.locale.t('obastatus.message.sponsor',
                           name = cluster.get('name'),
                           url = cluster.get('url'))

    try:
        await msg.finish([Plain(message), Image(str(cluster.get('banner')))])
    except Exception:
        await msg.finish(message)

@obastatus.command('version {{obastatus.help.version}}')
async def version(msg: Bot.MessageSession):
    await msg.finish(msg.locale.t('obastatus.message.version', version = await latestVersion()))